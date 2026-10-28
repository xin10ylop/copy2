# Step 2: per-wallet day stats from Enhanced-API histories (landed txs only; failed-tx fees added from RPC sampling).
import sys, os, json, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
TIPS = dict(json.load(open(os.path.join(C.OUTD, "tip_accounts.json"))))
FLAT_TIPS = {"BNAcDKtUhn1wtGDTjUh4j8Ahna35PQz67R2FThgh9aSt": "unk-flat", "tKq5esiQyvgRyfFa4JEz4uAUmppKyKB1PiQD9JhyGJY": "unk-flat",
             "D1Mc6j9xQWgR1o1Z7yU5nVVXFQiAYx7FG9AW1aVfwrUM": "unk-flat", "b1ooMngj7WbNPMZpWpnYRjxQ96RcDZ9ZFpRfjw1g7tg": "bloxroute?"}
PFR = set(json.load(open(os.path.join(C.OUTD, "pump_fee_recipients.json"))))
SERVICE = {"XTRDRDWmzDY7gNC1MvcBJW9uHXqbzruLAVoeFsoY2Hc"}
def tip_kind(a):
    if a in TIPS: return TIPS[a]
    if a in FLAT_TIPS: return FLAT_TIPS[a]
    l = a.lower()
    if l.startswith("node1"): return "node1"
    if l.startswith("speed"): return "speedlanding"
    if l.startswith("astra"): return "astralane"
    if l.startswith("noz") or l.startswith("temp"): return "nozomi"
    if l.startswith("next"): return "nextblock"
    return None
def parse(w, t):
    me = [a for a in t["accountData"] if a["account"] == w]
    delta = me[0]["nativeBalanceChange"] if me else 0
    fee = t["fee"] if t["feePayer"] == w else 0
    legs = collections.defaultdict(float); cp = {}; wsol = 0.0
    for x in t["tokenTransfers"]:
        if x["mint"] == C.WSOL:
            if x["toUserAccount"] == w: wsol += x["tokenAmount"]
            if x["fromUserAccount"] == w: wsol -= x["tokenAmount"]
            continue
        if x["toUserAccount"] == w: legs[x["mint"]] += x["tokenAmount"]; cp[x["mint"]] = x["fromUserAccount"]
        if x["fromUserAccount"] == w: legs[x["mint"]] -= x["tokenAmount"]; cp.setdefault(x["mint"], x["toUserAccount"])
    tips = 0; svc = 0; tk = collections.Counter(); curve = 0
    cps = set(cp.values())
    for x in t["nativeTransfers"]:
        if x["fromUserAccount"] != w: continue
        k = tip_kind(x["toUserAccount"])
        if k: tips += x["amount"]; tk[k] += x["amount"]
        elif x["toUserAccount"] in SERVICE: svc += x["amount"]
        elif x["toUserAccount"] in cps: curve += x["amount"]
    legs = {m: v for m, v in legs.items() if abs(v) > 0}
    pumpfee = any(cp.get(m) == C.bonding_curve(m) for m in legs)
    return dict(sig=t["signature"], ts=t["timestamp"], slot=t["slot"], delta=delta + int(wsol * 1e9), fee=fee, tips=tips, tk=tk, svc=svc,
                curve=curve, legs=legs, src=t["source"], typ=t["type"], pumpfee=pumpfee)
def stats(w, h, failed=None, creates_per_hour=3500.0):
    txs = sorted(list(reversed(h["txs"])), key=lambda t: t["slot"])
    if not txs: return None
    P = [parse(w, t) for t in txs]
    t0, t1 = h.get("cutoff_eff") or txs[0]["timestamp"], h["now"]
    if h["stop"] in ("maxpages", "error"): t0 = txs[0]["timestamp"]
    else: t0 = max(h["cutoff"], min(t["timestamp"] for t in txs) if h["stop"] == "end" else h["cutoff"])
    hours = (t1 - t0) / 3600
    trades = [p for p in P if p["legs"]]
    multi = sum(1 for p in trades if len(p["legs"]) > 1)
    buys = [p for p in trades if any(v > 0 for v in p["legs"].values())]
    sells = [p for p in trades if any(v < 0 for v in p["legs"].values()) and p not in buys]
    M = collections.OrderedDict()
    dirty = {m for p in trades if len(p["legs"]) > 1 for m in p["legs"]}
    allbought = {m for p in buys for m, v in p["legs"].items() if v > 0}
    pumpm = {m for p in buys if p["pumpfee"] and len(p["legs"]) == 1 for m in p["legs"]}
    for p in trades:
        if len(p["legs"]) != 1: continue
        for m, v in p["legs"].items():
            if m in dirty or m not in pumpm: continue
            d = M.setdefault(m, dict(cost=0, proc=0, tb=0.0, ts=0.0, fb=None, fs=None, nb=0, ns=0, pre=False))
            share = p["delta"] / len(p["legs"])
            if v > 0:
                d["cost"] += -share; d["tb"] += v; d["nb"] += 1
                if d["fb"] is None: d["fb"] = p["ts"]
            else:
                if d["fb"] is None: d["pre"] = True  # sold before any buy in window
                d["proc"] += share; d["ts"] += -v; d["ns"] += 1
                if d["fs"] is None: d["fs"] = p["ts"]
    mints = {m: d for m, d in M.items() if not d["pre"] and d["nb"] > 0}
    closed = {m: d for m, d in mints.items() if d["ts"] >= 0.99 * d["tb"]}
    held = {m: d for m, d in mints.items() if d["ts"] < 0.99 * d["tb"]}
    rets = [d["proc"] / d["cost"] - 1 for d in mints.values() if d["cost"] > 0]
    wins = sum(1 for d in mints.values() if d["proc"] > d["cost"])
    holds = [d["fs"] - d["fb"] for d in mints.values() if d["fs"] is not None]
    pnl_mints = sum(d["proc"] - d["cost"] for d in mints.values()) / 1e9
    nontrade_cost = sum(p["delta"] for p in P if not p["legs"] and (p["tips"] or (p["delta"] < 0 and -p["delta"] < 0.05e9))) / 1e9  # small non-trade outflows (fees/tips)
    fees = sum(p["fee"] for p in trades) / 1e9; tips = sum(p["tips"] for p in trades) / 1e9; svc = sum(p["svc"] for p in trades) / 1e9
    tk = collections.Counter()
    for p in trades: tk.update(p["tk"])
    sizes = [p["curve"] / 1e9 for p in buys if p["curve"]] or [(-p["delta"] - p["fee"] - p["tips"]) / 1e9 for p in buys]
    active_hours = len({p["ts"] // 3600 for p in buys})
    fail_fee = 0.0
    if failed: fail_fee = failed["n_failed"] * failed["mean_fee"] / 1e9
    res = dict(wallet=w, hours=hours, n_mints_all=len(allbought), n_dirty=len(dirty & allbought), n_pumpm=len(pumpm),
               clean_cost=sum(d["cost"] for d in mints.values()) / 1e9, stop=h["stop"], n_tx=len(P), n_buy=len(buys), n_sell=len(sells), multi=multi, mints=len(mints),
               med_size=st.median(sizes) if sizes else 0, out_buys=sum(-p["delta"] for p in buys) / 1e9, in_sells=sum(p["delta"] for p in sells) / 1e9,
               fees=fees, tips=tips, svc=svc, tip_kinds={k: round(v / 1e9, 4) for k, v in tk.most_common()},
               net_cash=sum(p["delta"] for p in trades) / 1e9, pnl_mints=pnl_mints, nontrade_cost=nontrade_cost,
               win=wins / len(mints) if mints else 0, med_ret=st.median(rets) if rets else 0, mean_ret=(sum(rets) / len(rets)) if rets else 0,
               med_hold=st.median(holds) if holds else None, p90_hold=sorted(holds)[int(.9 * len(holds))] if holds else None,
               held=len(held), held_cost=sum(d["cost"] - d["proc"] for d in held.values()) / 1e9,
               buys_per_h=len(buys) / hours if hours else 0, mints_per_active_h=len(mints) / active_hours if active_hours else 0, active_hours=active_hours,
               fail_fee=fail_fee, n_failed=(failed or {}).get("n_failed"), srcs=dict(collections.Counter(p["src"] for p in trades)))
    res["pick_rate"] = res["mints_per_active_h"] / creates_per_hour
    res["net_day"] = (pnl_mints - fail_fee) / hours * 24 if hours else 0
    res["mintmap"] = {m: dict(cost=d["cost"] / 1e9, proc=d["proc"] / 1e9, fb=d["fb"], fs=d["fs"], held=m in held) for m, d in mints.items()}
    return res
