# Shared helper for the create scan: Triton RPC (URL read from the old scratchpad's month/.triton_url, never printed,
# redacted in every error), a JSON cache under OUT/cache, and the pump event decoders (full layouts of
# crates/pump-codec/src/events.rs, trailing fields optional).
import json, os, time, hashlib, struct, base64, threading, urllib.request, gzip
TRI = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/month/.triton_url"
OUT = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallets/creates"
CACHE = OUT + "/cache"; os.makedirs(CACHE, exist_ok=True)
URL = open(TRI).read().strip(); TOKEN = URL.rsplit("/", 1)[-1]
PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"; PUMPSWAP = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
MINT_AUTH = "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"
WSOL = "So11111111111111111111111111111111111111112"; ZERO = "11111111111111111111111111111111"
T22_NATIVE = "9pan9bMn5HatX4EJdBwg9VgCa7Uz5HL8N1m5D3NdXejP"
SOL_LIKE = {WSOL, ZERO, T22_NATIVE, None}
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
TAG = bytes.fromhex("e445a52e51cb9a1d"); D_TRADE = bytes.fromhex("bddb7fd34ee661ee"); D_CREATE = bytes.fromhex("1b72a94ddeeb6376")
TXO = {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
_lock = threading.Lock(); _last = [0.0]; MIN_GAP = 0.008
def red(s): return str(s).replace(URL, "<rpc>").replace(TOKEN, "<token>")
def rpc(method, params, cache=True):
    h = hashlib.sha1(json.dumps([method, params], sort_keys=True).encode()).hexdigest()
    p = os.path.join(CACHE, h[:2], h + ".json.gz")
    if cache and os.path.exists(p):
        try: return json.load(gzip.open(p, "rt"))
        except Exception: pass
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    res = None
    for i in range(6):
        with _lock:
            w = _last[0] + MIN_GAP - time.time()
            if w > 0: time.sleep(w)
            _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}), timeout=60) as r: j = json.load(r)
            if "error" in j:
                e = red(j["error"])[:200]
                if "not available" in e or "skipped" in e.lower() or "not found" in e.lower(): res = None; break
                raise RuntimeError(e)
            res = j["result"]; break
        except Exception as e:
            if i == 5: raise RuntimeError(red(e)) from None
            time.sleep(1.0 * (i + 1))
    if cache and res is not None:
        os.makedirs(os.path.dirname(p), exist_ok=True); tmp = p + ".tmp%d" % threading.get_ident()
        with gzip.open(tmp, "wt", compresslevel=3) as f: json.dump(res, f)
        os.replace(tmp, p)
    return res
def tx(sig): return rpc("getTransaction", [sig, TXO])
def sigs(addr, before=None, until=None, limit=1000, cache=True):
    o = {"limit": limit, "commitment": "confirmed"}
    if before: o["before"] = before
    if until: o["until"] = until
    return rpc("getSignaturesForAddress", [addr, o], cache=cache) or []
# ---- base58
_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"; _IDX = {c: i for i, c in enumerate(_B58)}
def b58e(b):
    n = int.from_bytes(b, "big"); s = ""
    while n: n, r = divmod(n, 58); s = _B58[r] + s
    return "1" * (len(b) - len(b.lstrip(b"\0"))) + s
def b58d(s):
    n = 0
    for c in s: n = n * 58 + _IDX[c]
    b = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\0" * (len(s) - len(s.lstrip("1"))) + b
# ---- reader with optional trailing fields (bytes.rs opt_*: None when the buffer is exhausted)
class R:
    def __init__(s, d, o=0): s.d, s.o = d, o
    def left(s): return len(s.d) - s.o
    def u8(s): v = s.d[s.o]; s.o += 1; return v
    def u16(s): v = struct.unpack_from("<H", s.d, s.o)[0]; s.o += 2; return v
    def u32(s): v = struct.unpack_from("<I", s.d, s.o)[0]; s.o += 4; return v
    def u64(s): v = struct.unpack_from("<Q", s.d, s.o)[0]; s.o += 8; return v
    def i64(s): v = struct.unpack_from("<q", s.d, s.o)[0]; s.o += 8; return v
    def pk(s): v = b58e(s.d[s.o:s.o + 32]); s.o += 32; return v
    def st(s): n = s.u32(); v = s.d[s.o:s.o + n].decode("utf-8", "replace"); s.o += n; return v
    def opt(s, f): return f() if s.left() > 0 else None
def decode_create(d):   # d = bytes after the 8-byte event discriminator
    r = R(d); e = dict(name=r.st(), symbol=r.st(), uri=r.st(), mint=r.pk(), bonding_curve=r.pk(), user=r.pk(), creator=r.pk(),
                       ts=r.i64(), vtok=r.u64(), vsol=r.u64(), rtok=r.u64(), supply=r.u64())
    e["token_program"] = r.opt(r.pk); e["mayhem"] = r.opt(r.u8); e["cashback"] = r.opt(r.u8)
    e["quote_mint"] = r.opt(r.pk); e["vquote"] = r.opt(r.u64); e["creator_fee_bps"] = r.opt(r.u64)
    e["holder_reward"] = r.opt(r.u8); e["depth"] = r.opt(r.u8)
    return e
def decode_trade(d):
    r = R(d); e = dict(mint=r.pk(), sol=r.u64(), tok=r.u64(), is_buy=r.u8() == 1, user=r.pk(), ts=r.i64(), vsol=r.u64(), vtok=r.u64())
    try:
        e["rsol"] = r.opt(r.u64); e["rtok"] = r.opt(r.u64); r.opt(r.pk); e["fee_bps"] = r.opt(r.u64); e["fee"] = r.opt(r.u64)
        r.opt(r.pk); r.opt(r.u64); e["creator_fee"] = r.opt(r.u64); r.opt(r.u8); r.opt(r.u64); r.opt(r.u64); r.opt(r.u64); r.opt(r.i64)
        e["ix"] = r.opt(r.st); r.opt(r.u8)
        r.opt(r.u64); e["cashback"] = r.opt(r.u64); r.opt(r.u64); e["buyback_fee"] = r.opt(r.u64)
        if r.left() > 0: n = r.u32(); r.o += 34 * n           # shareholders
        e["quote_mint"] = r.opt(r.pk); e["quote_amount"] = r.opt(r.u64); e["vquote"] = r.opt(r.u64); e["rquote"] = r.opt(r.u64)
    except Exception:
        pass
    return e
def keys_of(t):
    return [k["pubkey"] if isinstance(k, dict) else k for k in t["transaction"]["message"]["accountKeys"]]
def events(t):
    """pump Create/Trade events of a jsonParsed tx, in order: [('create'|'trade', dict)]; inner emit_cpi first, logs fallback."""
    out = []; meta = t.get("meta") or {}
    for g in meta.get("innerInstructions") or []:
        for ix in g.get("instructions", []):
            if ix.get("programId") != PUMP or "data" not in ix: continue
            try: raw = b58d(ix["data"])
            except KeyError: continue
            if raw[:8] != TAG: continue
            try:
                if raw[8:16] == D_TRADE: out.append(("trade", decode_trade(raw[16:])))
                elif raw[8:16] == D_CREATE: out.append(("create", decode_create(raw[16:])))
            except Exception: pass
    if out: return out
    for line in meta.get("logMessages") or []:
        if line.startswith("Program data: "):
            try: raw = base64.b64decode(line[14:])
            except Exception: continue
            try:
                if raw[:8] == D_TRADE: out.append(("trade", decode_trade(raw[8:])))
                elif raw[:8] == D_CREATE: out.append(("create", decode_create(raw[8:])))
            except Exception: pass
    return out
def jdump(o, p):
    tmp = p + ".tmp"; json.dump(o, open(tmp, "w")); os.replace(tmp, p)
