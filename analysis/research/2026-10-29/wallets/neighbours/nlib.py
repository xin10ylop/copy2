# Shared helpers for the neighbours study: paths, the Triton RPC (URL read from the old session's month/.triton_url,
# never printed; errors redacted), a gzip cache of every response under this session's scratchpad, the bonding-curve
# PDA and the pump TradeEvent / CreateEvent decoder (the repo's rugsnipe_analysis.events).
import gzip, hashlib, json, os, sys, threading, time, urllib.request, urllib.error
sys.path.insert(0, "/home/user/copy2/analysis")
from rugsnipe_analysis import events as E

OLD = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
SP = OLD + "/fresh3/h9long"                      # wallet 4's study (read only)
OUT = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallets/neighbours"
CACHE = OUT + "/cache"; os.makedirs(CACHE, exist_ok=True)
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
_URL = None
def _url():
    global _URL
    if _URL is None: _URL = open(OLD + "/month/.triton_url").read().strip()
    return _URL
def red(s):
    u = _url(); return str(s).replace(u, "<url>").replace(u.rsplit("/", 1)[-1], "<token>")
_lock = threading.Lock(); _last = [0.0]; GAP = float(os.environ.get("GAP", "0.03"))
def rpc(method, params, cache=True):
    h = hashlib.sha1(json.dumps([method, params]).encode()).hexdigest(); p = os.path.join(CACHE, h[:2], h + ".json.gz")
    if cache and os.path.exists(p):
        with gzip.open(p, "rt") as f: return json.load(f)
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for i in range(7):
        with _lock:
            w = _last[0] + GAP - time.time()
            if w > 0: time.sleep(w)
            _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(_url(), body, {"Content-Type": "application/json"}), timeout=60) as r:
                j = json.load(r)
            if "error" in j: raise RuntimeError(red(j["error"])[:200])
            res = j["result"]; break
        except Exception as e:
            if i == 6: raise RuntimeError(red(e)[:200]) from None
            time.sleep(1.0 * (i + 1))
    if cache and res is not None:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with gzip.open(p + ".tmp", "wt") as f: json.dump(res, f)
        os.replace(p + ".tmp", p)
    return res
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
def tx(sig): return rpc("getTransaction", [sig, TXO])
def sigs(addr, before=None, until=None, limit=1000, cache=True):
    o = {"limit": limit}
    if before: o["before"] = before
    if until: o["until"] = until
    return rpc("getSignaturesForAddress", [addr, o], cache=cache) or []

A58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58d(d): return E.b58decode(d)
def b58e(b): return E.b58encode(b)
_P = 2**255 - 19; _D = (-121665 * pow(121666, _P - 2, _P)) % _P
def _on_curve(b):
    y = int.from_bytes(b, "little") & ((1 << 255) - 1)
    if y >= _P: return False
    y2 = y * y % _P; u = (y2 - 1) % _P; v = (_D * y2 + 1) % _P
    x2 = u * pow(v, _P - 2, _P) % _P
    return x2 == 0 or pow(x2, (_P - 1) // 2, _P) == 1
def bonding_curve(mint):
    pid = b58d(PUMP)
    for bump in range(255, -1, -1):
        h = hashlib.sha256(b"bonding-curve" + b58d(mint) + bytes([bump]) + pid + b"ProgramDerivedAddress").digest()
        if not _on_curve(h): return b58e(h)
def keys(t):
    la = t["meta"].get("loadedAddresses") or {}
    return t["transaction"]["message"]["accountKeys"] + la.get("writable", []) + la.get("readonly", [])
def parse(t, mint):
    """compact record of one curve transaction: payer, err, slot, index, time, pump trades of this mint
    [user, is_buy, token_amount, virtual_token_reserves_after, ix_name], and whether it holds the coin's CreateEvent"""
    ks = keys(t); tr = []; create = False
    for g in t["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != PUMP: continue
            raw = b58d(ix.get("data", ""))
            if raw[:8] != E.EVENT_IX_TAG: continue
            if raw[8:16] == E.DISC_TRADE:
                try: e = E.decode_trade(raw[8:])
                except Exception: continue
                if e.mint == mint: tr.append([e.user, int(e.is_buy), e.token_amount, e.virtual_token_reserves, e.ix_name])
            elif raw[8:16] == E.DISC_CREATE:
                try: c = E.decode_create(raw[8:])
                except Exception: continue
                if c.mint == mint: create = True
    return dict(payer=ks[0], err=t["meta"]["err"] is not None, s=t["slot"], i=t.get("transactionIndex"),
                bt=t.get("blockTime"), tr=tr, create=create)
