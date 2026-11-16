# The copy model the wallet hunt shares (screen.py, step2_model.py): the frozen live setup with any wallet as the
# leader. prep(path, index of its buy, SOL per quote unit, landing) -> arrays; model(prepared) -> (net SOL, why).
import numpy as np
ME = "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"
def prep(tr, k, rate, n, pmax=1.25):
    its = tr[k]; L = tr[k]["user"]; vta = its["vt"]; t0 = its["t"]
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1]) if n == "slot+1" else min(k + n, len(tr) - 1)
    ent = tr[j]; rest = tr[j + 1:]
    other = np.array([e["user"] not in (L, ME) for e in rest], dtype=bool); sell = np.array([not e["buy"] for e in rest], dtype=bool)
    return dict(refused=(vta / ent["vt"]) ** 2 > pmax, rate=rate, ent=(ent["vt"], ent["vq"], ent["bps"]), hopf=1.0,
                px=np.array([(vta / e["vt"]) ** 2 for e in rest]),
                age=np.array([e["t"] - t0 for e in rest], dtype=float), sell=np.array([e["user"] == L and not e["buy"] for e in rest], dtype=bool),
                grad=np.array([e.get("real") == 0 for e in rest], dtype=bool), vt=np.array([float(e["vt"]) for e in rest]),
                vq=np.array([float(e["vq"]) for e in rest]), bps=np.array([float(e["bps"]) for e in rest]), last=ent["t"] - t0,
                osell=other & sell, obuy=other & ~sell)
def first(c):
    i = int(np.argmax(c)) if len(c) else 0
    return i if len(c) and c[i] else None
def model(p, stake=0.5, tp=4.0, hold=600, early=(30, 290, 1.5)):
    if p["refused"]: return -0.0004, "refused"
    vt0, vq0, bps0 = p["ent"]; Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    n = len(p["px"])
    def out(ex):
        if ex is None: vq, vt, b = vq0, vt0, bps0
        else: vq, vt, b = p["vq"][ex], p["vt"][ex], p["bps"][ex]
        vq_r = vq + net_in; vt_r = vt * vq / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026
    if n == 0: return out(None), "time"
    px, age = p["px"], p["age"]; c = []
    i = first(p["grad"]); c += [(i, 0, "graduated", 0)] if i is not None else []
    if early:
        i = first(p["sell"] & (age >= early[0]) & (age < early[1]) & (px < early[2])); c += [(i, 1, "its_sell", 1)] if i is not None else []
    i = first(px >= tp); c += [(i, 2, "tp", 1)] if i is not None else []
    lo = np.searchsorted(age, age - 60, side="left"); s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])])
    i = first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30)); c += [(i, 3, "sell_pressure", 1)] if i is not None else []
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    i = first((pk >= 1.0) & (age - lasthi >= 180)); c += [(i, 3, "stall", 1)] if i is not None else []
    i = first(age >= hold); c += [(i, 4, "time", 0)] if i is not None else []
    if not c: return out(n - 1), "time"
    i, _, why, d = min(c); return out(min(i + d, n - 1)), why
