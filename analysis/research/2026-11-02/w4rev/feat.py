# Create-time features of each routable create (step 2): from the create transaction only (what a bot sees when it
# lands in the create slot), plus the creator's earlier creates in the quote-control universe since Oct 19.
import os, sys, re, time, collections
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, routes
P1_END = 1792713600        # 2026-10-23 00:00 UTC: P1 = Oct 19-22, P2 = Oct 23-26 (+ Oct 27 00:00..00:40 of the trips)
def per(bt): return "P1" if bt < P1_END else "P2"
def load_universe(path):
    U = lib.jl(path)
    rows = [dict(r) for s, r in U.items() if r.get("mint")]
    routes.ensure([r["quote"] for r in rows])
    for r in rows: r["cls"] = routes.cls(r["quote"])
    return rows
def host(u):
    try: h = urlparse(u).netloc.lower()
    except Exception: h = ""
    return h or ("(none)" if not u else "(other)")
def base(r):
    """create-tx features"""
    v0 = r.get("vquote") or r.get("vsol") or 1
    buys = [d for d in r["dev"] if d[1]]
    dq = sum((d[4] if d[4] is not None and r.get("vquote") else d[2]) or 0 for d in buys)
    f = dict(cls=r["cls"], quote=r["quote"], depth=r.get("depth") or 0,
             dev_sol=round(30.0 * dq / v0, 4), dev_n=len(buys), dev_users=len({d[0] for d in buys}),
             dev_tok=round(sum(d[3] for d in buys) / 1e15, 5),
             dev_other=int(any(d[0] != r["user"] for d in buys)),
             cre_is_user=int(r["creator"] == r["user"]), payer_is_user=int(r["payer"] == r["user"]),
             cashback=r.get("cashback"), mayhem=r.get("mayhem"), cfee=r.get("cfee"),
             host=host(r.get("uri") or ""), hour=time.gmtime(r["cbt"]).tm_hour,
             nlen=len(r["name"]), slen=len(r["sym"]), s_upper=int(r["sym"].isupper()), s_eq_n=int(r["sym"].lower() == r["name"].lower()),
             nonascii=int(any(ord(ch) > 127 for ch in r["name"] + r["sym"])), digits=int(bool(re.search(r"\d", r["name"] + r["sym"]))),
             nwords=len(r["name"].split()), progs="+".join(sorted(p[:6] for p in (r.get("progs") or []))), nsig=r.get("nsig"),
             cu=r.get("cu"), fee=r.get("fee"), cidx=r.get("cidx"))
    return f
def creator_hist(rows):
    """for each create (by sig): the same signer's earlier creates in rows (count, last 24 h, and the gap to the last)"""
    by = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: (r["cslot"], r.get("cidx") or 0)): by[r["user"]].append(r)
    out = {}
    for u, L in by.items():
        for i, r in enumerate(L):
            prev = L[:i]
            out[r["csig"]] = dict(prior=len(prev), prior24=sum(1 for p in prev if p["cbt"] >= r["cbt"] - 86400),
                                  gap=(r["cbt"] - prev[-1]["cbt"]) if prev else None, prior_same_q=sum(1 for p in prev if p["quote"] == r["quote"]))
    return out
