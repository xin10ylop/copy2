# Re-price stage-3 trips at our live speed (copy2: wallet 4's copy, Oct 28-29, deploy-frankfurt.md trade table): sent in
# 3-6 ms, landed in its own slot or at the top of the next block, with 2-13 trades of the coin between its trade and
# ours (median 4). So our buy fills on the pool state after the K-th trade of the coin on the same pool behind its buy
# (counted in its own block, then the next blocks), and each of our sales K trades behind each of its sales.
#   constant-product pool or pump curve (its own trade leaves the marginal price above its average on a buy, below on a
#     sale): the reserves after that K-th trade give the price; anything else: the next other trade on our side at or
#     after that point (its average price); none in 3 slots: unpriced
#   our impact (1 + X/Q): X our stake in the pool's quote, Q the pool's quote reserve at that state (+30 SOL / 279.9M
#     tokens of virtual reserves on a pump curve)
# Costs on a 1 SOL stake as before: 0.0095 SOL a transaction (buy + up to 3 sales) + 1.25% each way.
#   K=4 python3 -I rescore2.py DIR_IN DIR_OUT [WALLET8 ...]
import json, glob, os, sys, time, gzip, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor

IN, OUT = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else (None, None); ONLY = sys.argv[3:]
K = int(os.environ.get('K', '4'))
U = open("/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/month/.triton_url").read().strip()
WSOL = "So11111111111111111111111111111111111111112"
SOLUSD, MAX_SELLS, AHEAD = 96.0, 4, 3
VSOL, VTOK = 30.0, 73_000_000.0             # pump.fun curve: virtual reserves on top of the curve's balances (its token
                                            # balance holds the 206.9M kept for migration: 1,073M virtual - 1,000M; G4)
lock, last = threading.Lock(), [0.0]

def rpc(m, p):
    err = ""
    for i in range(6):
        with lock:
            dt = time.time() - last[0]
            if dt < 0.06: time.sleep(0.06 - dt)
            last[0] = time.time()
        try:
            req = urllib.request.Request(U, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(),
                                         {"Content-Type": "application/json", "Accept-Encoding": "gzip"})
            r = urllib.request.urlopen(req, timeout=60); raw = r.read()
            j = json.loads(gzip.decompress(raw) if r.headers.get("Content-Encoding") == "gzip" else raw)
            if "error" in j:
                if j["error"].get("code") in (-32007, -32009): return None
                raise RuntimeError(str(j["error"])[:120])
            return j["result"]
        except Exception as e:
            err = str(e).replace(U, "<url>")[:120]; time.sleep(1.5 * (i + 1))
    print("rpc failed", m, err, flush=True); return None

def pools(tx, mint):
    """[(pool, avg price, quote, quote size, coin size, side, Q after, C after)] for the coin's non-signer pool owners."""
    meta = tx["meta"]; tr = tx["transaction"]
    raw = tr.get("accountKeys") or tr.get("message", {}).get("accountKeys") or []
    if raw and isinstance(raw[0], dict):
        keys = [k["pubkey"] for k in raw]; signers = {k["pubkey"] for k in raw if k.get("signer")}
    else:
        keys = list(raw); n = (tr.get("message", {}).get("header") or {}).get("numRequiredSignatures", 1); signers = set(keys[:n])
    if meta.get("loadedAddresses"): keys += meta["loadedAddresses"].get("writable", []) + meta["loadedAddresses"].get("readonly", [])
    ch, post = {}, {}
    for side, sign in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            o = b.get("owner")
            if not o or o in signers: continue
            m = b["mint"]; v = float(b["uiTokenAmount"]["uiAmount"] or 0)
            ch.setdefault(o, {}); ch[o][m] = ch[o].get(m, 0.0) + sign * v
            if sign > 0: post.setdefault(o, {}); post[o][m] = post[o].get(m, 0.0) + v
    out = []
    for o, m in ch.items():
        dc = m.get(mint, 0.0)
        if abs(dc) <= 0: continue
        lam = None
        if o in keys:
            i = keys.index(o); d_l = (meta["postBalances"][i] - meta["preBalances"][i]) / 1e9
            if d_l * dc < 0: lam = (d_l, meta["postBalances"][i] / 1e9)
        cands = [(k, v) for k, v in m.items() if k != mint and v * dc < 0]
        if lam: cands.append(("SOL(curve)", lam[0]))
        if not cands: continue
        q, dq = max(cands, key=lambda kv: abs(kv[1]))
        C = (post.get(o, {}).get(mint, 0.0))
        if q == "SOL(curve)": Q, C = lam[1] + VSOL, C + VTOK; qn = WSOL
        else: Q, qn = post.get(o, {}).get(q, 0.0), q
        if Q <= 0 or C <= 0: continue
        out.append((o, abs(dq) / abs(dc), qn, abs(dq), abs(dc), "buy" if dc < 0 else "sell", Q, C))
    return sorted(out, key=lambda x: -x[4])

TXC, BLK = {}, {}
def tx_of(sig):
    if sig not in TXC: TXC[sig] = rpc("getTransaction", [sig, {"encoding": "json", "maxSupportedTransactionVersion": 1}])
    return TXC[sig]

def trades_in(slot, mint):
    key = (slot, mint)
    if key in BLK: return BLK[key]
    b = rpc("getBlock", [slot, {"encoding": "json", "transactionDetails": "accounts", "rewards": False, "maxSupportedTransactionVersion": 1}])
    out = []
    for tx in (b or {}).get("transactions") or []:
        if tx["meta"].get("err"): continue
        if not any(x.get("mint") == mint for x in (tx["meta"].get("postTokenBalances") or [])): continue
        sg = {k["pubkey"] for k in tx["transaction"]["accountKeys"] if isinstance(k, dict) and k.get("signer")}
        sigs = set(tx["transaction"].get("signatures") or [])
        for p in pools(tx, mint)[:1]: out.append((sg, sigs, p))
    BLK[key] = out
    return out

def fit_curve(trades):
    """Virtual reserves (a, b) on top of a pool's real ones, from its trades: on a constant-product curve every trade
    keeps (Q + a)(C + b) fixed, one linear equation per trade: a*dc - b*dq = dq*C_after - Q_before*dc. Returns (a, b,
    worst error of the fitted curve on those trades' average prices), or None."""
    rows = []
    for p in trades:
        _, avg, q, dq, dc, side, Q, C = p
        Qb = Q - dq if side == "buy" else Q + dq
        w = 1.0 / (dq * C)
        rows.append((dc * w, -dq * w, (dq * C - Qb * dc) * w, p, Qb))
    if len(rows) < 2: return None
    s11 = sum(r[0] * r[0] for r in rows); s12 = sum(r[0] * r[1] for r in rows); s22 = sum(r[1] * r[1] for r in rows)
    t1 = sum(r[0] * r[2] for r in rows); t2 = sum(r[1] * r[2] for r in rows); det = s11 * s22 - s12 * s12
    if abs(det) <= 1e-9 * s11 * s22: return None                # the trades cannot separate a from b
    A = (t1 * s22 - t2 * s12) / det; B = (s11 * t2 - s12 * t1) / det
    err = 0.0
    for _, _, _, p, Qb in rows:
        _, avg, q, dq, dc, side, Q, C = p
        Cb = C + dc if side == "buy" else C - dc
        if Qb + A <= 0 or Cb + B <= 0: return None
        pred = (Qb + A + dq) / (Cb + B) if side == "buy" else (Qb + A - dq) / (Cb + B)
        err = max(err, abs(pred / avg - 1))
    return A, B, err

def our_size(tx, owner, q, dq, want, x_sol_ratio):
    """1 SOL of ours in the pool's quote: exactly 1 on a SOL pool; else its quote per SOL it paid (or got) in this
    transaction (its first buy only, not its add-ons, G7's finding); else its USD size as before"""
    if q == WSOL: return 1.0
    meta = tx["meta"]; tr = tx["transaction"]
    raw = tr.get("accountKeys") or tr.get("message", {}).get("accountKeys") or []
    keys = [k["pubkey"] if isinstance(k, dict) else k for k in raw]
    if owner in keys:
        i = keys.index(owner); d = (meta["postBalances"][i] - meta["preBalances"][i] + (meta.get("fee") or 0)) / 1e9
        sol = -d if want == "buy" else d
        if sol > 0.05: return dq / sol
    return dq * x_sol_ratio

def leg(sig, owner, mint, want, x_sol_ratio, K=K, X=None, skip=()):
    """(its average price, our price, slots behind, our base price / its price, our impact per SOL of stake), or
    "unpriced", or None (its transaction not found). X: our size in the pool's quote (default: x_sol_ratio of its)."""
    tx = tx_of(sig)
    if not tx: return None
    ps = pools(tx, mint)
    if not ps: return None
    own = ps[0]; pool, mine, q, dq, dc, side, Q, C = own
    if X is None: X = our_size(tx, owner, q, dq, want, x_sol_ratio)   # our 1 SOL in the pool's quote units
    slot, seq, found = tx["slot"], [], False
    for k in range(0, AHEAD + 1):
        for sg, sigs, p in trades_in(slot + k, mint):
            if sig in sigs: found = True; continue
            if k == 0 and not found: continue                 # trades ahead of it in its own block
            if sg & set(skip): continue
            if p[0] == pool and p[2] == q: seq.append((k, sg, p))
        if k == 0 and not found: return None
        if len(seq) >= K + 10: break
    at = seq[min(K, len(seq)) - 1] if K and seq else None     # the K-th trade behind it (the last seen, if fewer)
    f = fit_curve([own] + [p for _, _, p in seq[:K + 10]])
    if f and f[2] < 0.03:                                     # a constant-product curve (virtual reserves a, b)
        A, B, _ = f
        Qs, Cs = (at[2][6], at[2][7]) if at else (Q, C)
        Qs, Cs = Qs + A, Cs + B
        base, k_land = Qs / Cs, (at[0] if at else 0)
    else:                                                     # anything else: the next trade on our side, as it paid
        hit = next(((k, p) for k, sg, p in seq[max(K - 1, 0):] if owner not in sg and p[5] == want
                    and p[3] >= 0.02 * dq and 0.25 < p[1] / mine < 4), None)
        if not hit: return "unpriced"
        k_land, base, Qs = hit[0], hit[1][1], None
    imp1 = X / Qs if Qs else 0.0                              # our impact per 1 SOL of stake: (1 + stake * imp1)
    ours = base * (1 + imp1) if want == "buy" else base / (1 + imp1)
    return mine, ours, k_land, base / mine, imp1

def score(w, t):
    usd0 = t.get("usd0") or t["usd_in"]
    ratio = (SOLUSD / usd0) if usd0 > 0 else 1.0               # our SOL against its first buy's SOL value
    e = leg(t["sig0"], w, t["mint"], "buy", ratio)
    if not e or e == "unpriced": return None
    r_in = e[1] / e[0]
    legs = []                                                  # per sale: its fraction, its price, base ratio, impact per SOL
    gross, used = 0.0, 0.0
    sells = sorted(t["sells"], key=lambda s: -s["frac"])
    for s in sells[:MAX_SELLS]:
        x = leg(s["sig"], w, t["mint"], "sell", ratio)
        if x == "unpriced": return None
        r_out = x[1] / x[0] if x else 0.9
        legs.append((s["frac"], s["px"], x[3] if x else 0.9, x[4] if x else e[4]))
        gross += s["frac"] * (s["px"] * r_out) / (t["px0"] * r_in); used += s["frac"]
    for s in sells[MAX_SELLS:]:
        gross += s["frac"] * s["px"] * 0.97 / (t["px0"] * r_in)
    ntx = 1 + min(len(t["sells"]), 3)
    return dict(copy=gross - 1 - 0.0095 * ntx - 0.0125 * (1 + max(gross, 0)), entry_ratio=r_in, entry_slot=e[2],
                entry_base=e[3], entry_imp1=e[4], legs=legs,
                its_pct=(t["usd_out"] - t["usd_in"]) / t["usd_in"] if t["usd_in"] else 0.0)

if __name__ == '__main__' and IN:
  os.makedirs(OUT, exist_ok=True)
  for f in sorted(glob.glob(f"{IN}/*.json")):
      try: d = json.load(open(f))
      except Exception: continue                            # still being written
      w = d["wallet"]; fn = f"{OUT}/{w}.json"
      if (ONLY and w[:8] not in ONLY) or os.path.exists(fn): continue
      qsyms = {t.get("quote") for t in d["trips"]} - {None, "WSOL", "SOL"}
      for t in d["trips"]:                                    # a route's quote token taken for the coin (G7)
          if t.get("sym") in qsyms: t["skip"] = "quote token"
      with ThreadPoolExecutor(4) as ex:
          res = list(ex.map(lambda t: None if t.get("skip") else score(w, t), d["trips"]))
      for t, r in zip(d["trips"], res): t["s2_old"] = t.get("s2"); t["s2"] = r
      json.dump(d, open(fn, "w"))
      ok = [t for t in d["trips"] if t["s2"]]
      print(time.strftime("%H:%M:%S"), w[:8], len(ok), "priced; copy with our impact %+.2f SOL (before %+.2f)" %
            (sum(t["s2"]["copy"] for t in ok), sum((t["s2_old"] or {}).get("copy", 0) for t in ok)), flush=True)
      TXC.clear(); BLK.clear()
