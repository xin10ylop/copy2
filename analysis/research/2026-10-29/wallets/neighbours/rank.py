# Who buys wallet 4's coins in the create slot or the next: every trader (full address, from the fetched curve windows of
# fetch.py) that bought in slot C or C + 1 of the coins of wallet 4's 1.45+ SOL buys (C = the slot of the coin's
# CreateEvent). The create transaction's own trades (the dev buy) are left out. Per trader, over the coins it bought early:
#   coins (other-quote coins), share at C+0 / C+1, share before wallet 4's buy, median slot gap to it,
#   buy size in SOL: K * (1/v_after - 1/v_before), K = wallet 4's SOL value / (1/vt_after - 1/vt_before) on the same coin,
#   failed: its failed transactions on the curve in the window / all its transactions there,
#   frenzy: other traders' landed buys in the 2 slots after its buy (slots b+1, b+2),
#   hold: its first sale of the coin after its first early buy: the fetched window (complete up to slot max(C+3, S+2)),
#         then wallet 4's path (full_paths.py: every trade from wallet 4's buy to its sale, sampled when over 40),
#   win: at that first sale, the average sale price / its average buy price (gross, no fees) > 1; when no sale is seen
#         before wallet 4's sale, the marginal price at wallet 4's sale / its average buy price (marked),
#   days: coins on Oct 27-28 (wallet 4's buy time >= Oct 27 00:00 UTC).
#   python3 -I rank.py [MIN_COINS]   ->  out/rank.txt (printed), OUT/rank.json
import sys, os, json, statistics, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nlib as L
HERE = os.path.dirname(os.path.abspath(__file__))
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 5
WIN = json.load(open(L.OUT + "/win.json"))
P = json.load(open(f"{L.SP}/H9kuqGKN_fpaths.json")); G = json.load(open(f"{L.SP}/H9kuqGKN_gpaths.json"))
T = {x["m"]: x for x in json.load(open(f"{L.SP}/H9kuqGKN_trips.json"))}
Q = json.load(open(f"{L.SP}/H9kuqGKN_quote.json"))
LATE = 1793059200          # 2026-10-27 00:00 UTC
NAMED = {"6anjqMeW": "6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc", "AMDEmVoc": "AMDEmVocLtN5ji2gBY7BrmSHEyM5vt6TGszBbg4crMXg",
         "Fhbh1DTU": "Fhbh1DTUDKt6qu9zVg8Q5VgnZa1WWWbxBxG6pCoJoggA", "dKMjeGJ4": "dKMjeGJ4Mk9S3hxdfTThvZ7exks2xMwWqSM5NvN2CTK"}
def med(a): return statistics.median(a) if a else None
def pct(a, q):
    a = sorted(a); return a[min(len(a) - 1, int(len(a) * q))] if a else None

E = collections.defaultdict(list)          # trader -> list of per-coin records
W4 = []                                    # wallet 4's own per-coin record (offset, frenzy)
cal = []                                   # K against the SOL curve's K (SOL-quote coins)
bad = collections.Counter()
for m, v in WIN.items():
    if "err" in v: bad[v["err"]] += 1; continue
    C, S, iw, end = v["C"], v["S"], v["i"] or 0, v["end"]
    if v["pre_capped"]: bad["pre capped"] += 1; continue
    K = v["v"] / (1 / v["vt"] - 1 / (v["vt"] + v["tok"]))
    if v["kind"] == "pump, SOL quote": cal.append(K / (30 * 1.073e15))     # 30 SOL x 1,073M tokens (6 decimals), in SOL
    rows, failed, ntx = [], collections.Counter(), collections.Counter()
    for t in v["tx"]:
        if t["err"]: failed[t["payer"]] += 1; ntx[t["payer"]] += 1; continue
        users = set()
        for u, b, tok, va, ix in t["tr"]:
            rows.append((t["s"], t["i"] or 0, u, b, tok, va, t["bt"], t["create"])); users.add(u)
        for u in users or {t["payer"]}: ntx[u] += 1
    def frenzy(slot, who):
        return sum(1 for r in rows if r[3] and r[2] != who and slot + 1 <= r[0] <= slot + 2)
    W4.append(dict(m=m, off=S - C, fr=frenzy(S, L.W), late=v["bt"] >= LATE, other="other" in v["kind"]))
    path = (P.get(m) or G.get(m) or {}).get("path") or []
    sampled = (P.get(m) or {}).get("sampled", False) or (m in G)
    x = T[m]
    if m in G: w4_state, w4_sbt = path[-1][5] if path else None, None
    else: s4 = x["tr"][1]; w4_state, w4_sbt = s4["vt"] - s4["tok"], s4["bt"]
    seen = set()
    for r in rows:
        s, i, u, b, tok, va, bt, cr = r
        if not b or cr or u == L.W or u in seen or s not in (C, C + 1): continue
        seen.add(u)
        vb = va + tok
        buys = [q for q in rows if q[2] == u and q[3] and q[0] in (C, C + 1) and not q[7]]
        size1 = K * (1 / va - 1 / vb); size_all = sum(K * (1 / q[5] - 1 / (q[5] + q[4])) for q in buys)
        tok_all = sum(q[4] for q in buys)
        avg_buy = sum((1 / q[5] - 1 / (q[5] + q[4])) for q in buys) / tok_all          # in K units per token
        # its first sale after this buy: window rows (full addresses), then the path (8-char prefixes) after the window
        sell = next((q for q in rows if q[2] == u and not q[3] and (q[0], q[1]) > (s, i)), None)
        src = "window"
        if not sell:
            sell = next((q for q in path if q[2] == u[:8] and not q[3] and q[0] > end), None); src = "path"
        rec = dict(m=m, off=s - C, before=(s, i) < (S, iw), gap=s - S, size=size1, size_all=size_all, fr=frenzy(s, u),
                   fail=failed.get(u, 0), ntx=ntx.get(u, 0), late=v["bt"] >= LATE, other="other" in v["kind"], q=Q.get(m, "?"),
                   bt=bt or v["bt"], sampled=sampled)
        if sell:
            ss, si, su, sb, stok, sva, sbt = sell[:7]
            avg_sell = (1 / (sva - stok) - 1 / sva) / stok if sva - stok > 0 else 0
            rec.update(sold=True, hold_s=(sbt - bt) if sbt and bt else None, hold_slots=ss - s, mult=avg_sell / avg_buy,
                       sell_src=src, sold_part=stok / tok_all)
        else:
            mark = (1 / w4_state ** 2) / avg_buy if w4_state else None
            rec.update(sold=False, mark=mark)
        E[u].append(rec)

def summary(u, recs):
    n = len(recs); sz = [r["size"] for r in recs]
    sold = [r for r in recs if r["sold"]]; hs = [r["hold_s"] for r in sold if r["hold_s"] is not None]
    flip = sum(1 for r in sold if r["hold_s"] is not None and r["hold_s"] <= 5)
    unsold_full = sum(1 for r in recs if not r["sold"] and not r["sampled"])       # path complete: held past wallet 4's sale
    won = sum(1 for r in sold if r["mult"] > 1); marked = [r for r in recs if not r["sold"] and r.get("mark")]
    wonm = sum(1 for r in marked if r["mark"] > 1)
    return dict(addr=u, coins=n, other=sum(r["other"] for r in recs), big=sum(1 for r in recs if r["size"] >= 0.45),
                c0=sum(r["off"] == 0 for r in recs) / n, before=sum(r["before"] for r in recs) / n, gap=med([r["gap"] for r in recs]),
                size=med(sz), size_p90=pct(sz, 0.9), fail=sum(r["fail"] for r in recs), ntx=sum(r["ntx"] for r in recs),
                fr=med([r["fr"] for r in recs]), sold=len(sold), flip=flip, hold=med(hs), hold_p25=pct(hs, 0.25), hold_p75=pct(hs, 0.75),
                held_past=unsold_full, won=won, marked=len(marked), wonm=wonm, mult=med([r["mult"] for r in sold]),
                late=sum(r["late"] for r in recs), first=min(r["bt"] for r in recs), last=max(r["bt"] for r in recs),
                quotes=collections.Counter(r["q"] for r in recs).most_common(3))
SUM = {u: summary(u, r) for u, r in E.items()}
def ts(t): return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d")
def line(s, full=False):
    a = s["addr"] if full else s["addr"][:8]
    hold = f"{s['hold']:.0f}" if s["hold"] is not None else "-"
    win = f"{s['won']}/{s['sold']}" + (f" +{s['wonm']}/{s['marked']}m" if s["marked"] else "")
    return (f"{a:{44 if full else 8}s} {s['coins']:4d} {s['other']:4d} {s['big']:4d} {s['c0']:5.0%} {s['before']:5.0%} {s['gap']:+4.0f} "
            f"{s['size']:6.3f} {s['size_p90']:6.3f} {s['fail']:4d}/{s['ntx']:<4d} {s['fr']:4.0f} {s['sold']:4d} {s['flip']:4d} {hold:>6s} "
            f"{s['held_past']:4d} {win:>13s} {s['late']:4d} {ts(s['first'])}..{ts(s['last'])}")
HEAD = (f"{'trader':8s} coins othr >=.45 at+0 befW4 gap  sizeSOL   p90 fail/txs  frz sold flip hold_s held   won(sold+mark) 27-28 dates")
if __name__ == "__main__":
    ok = [v for v in WIN.values() if "err" not in v]
    print(f"coins fetched {len(WIN)}, usable {len(ok) - bad['pre capped']}, skipped {dict(bad)}")
    print(f"create slot from the CreateEvent on {sum(v['C_from'] == 'create event' for v in ok)} of {len(ok)}")
    off = collections.Counter(min(w['off'], 3) for w in W4)
    print(f"wallet 4's buy slot - create slot: " + ", ".join(f"+{k}{'+' if k == 3 else ''} {c}" for k, c in sorted(off.items())) + f" (of {len(W4)})")
    print(f"  other-quote coins only: " + ", ".join(f"+{k} {c}" for k, c in sorted(collections.Counter(min(w['off'], 3) for w in W4 if w['other']).items())))
    print(f"wallet 4's frenzy (others' buys in its slot +1..+2): median {med([w['fr'] for w in W4])}, p25 {pct([w['fr'] for w in W4], .25)}, p75 {pct([w['fr'] for w in W4], .75)}")
    print(f"size calibration, SOL-quote coins: K / (30 SOL x 1,073M tokens) median {med(cal):.4f} p10 {pct(cal, .1):.4f} p90 {pct(cal, .9):.4f} (n {len(cal)})")
    print(f"traders that bought at C+0/C+1 on at least one coin: {len(SUM)}; on {MIN}+ coins: {sum(1 for s in SUM.values() if s['coins'] >= MIN)}")
    print()
    print("columns: coins (other-quote coins, coins with an early buy >= 0.45 SOL), share at C+0, share before wallet 4's buy, median slot gap to its buy,")
    print("median / p90 first early buy SOL, failed / all its txs on the curve in the window, median frenzy, sales seen, flips (<= 5 s),")
    print("median hold s (p25-p75 below), coins held past wallet 4's sale (unsampled path), won at its first sale (+ won marked at wallet 4's sale),")
    print("coins on Oct 27-28, first..last coin date")
    print(HEAD)
    rank = sorted(SUM.values(), key=lambda s: -s["coins"])
    for s in rank:
        if s["coins"] < MIN: break
        print(line(s))
    print()
    print("TOP 15 by coins with an early buy >= 0.45 SOL")
    print(HEAD.replace("trader  ", "trader" + " " * 38))
    top = sorted(SUM.values(), key=lambda s: (-s["big"], -s["coins"]))[:15]
    for s in top: print(line(s, True))
    print()
    print("THE FOUR NAMED IN wallet-check.md")
    for k, a in NAMED.items():
        print(line(SUM[a], True) if a in SUM else f"{a} not among the early buyers")
    for s in top + [SUM[a] for a in NAMED.values() if a in SUM]:
        print(f"  {s['addr'][:8]} hold p25/p75 {s['hold_p25']}/{s['hold_p75']} s, median sale multiple {s['mult'] and round(s['mult'], 3)}, quotes {s['quotes']}")
    w4 = dict(coins=len(W4), other=sum(w["other"] for w in W4), late=sum(w["late"] for w in W4), fr=med([w["fr"] for w in W4]),
              c0=sum(w["off"] == 0 for w in W4) / len(W4))
    print(f"wallet 4 on these coins: {w4}")
    json.dump(dict(w4=w4, sum=SUM, top=[s["addr"] for s in top], named=NAMED, recs={u: E[u] for u in [s["addr"] for s in top] + list(NAMED.values()) if u in E}),
              open(L.OUT + "/rank.json", "w"))
