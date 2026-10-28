# Shared helpers. KEY is read at runtime from live/rivals2.py via ast (never printed).
import ast, json, os, time, urllib.request, urllib.error, hashlib, threading, base64
LIVE = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/live/rivals2.py"
OUTD = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/rivalpnl"
CACHE = os.path.join(OUTD, "cache")
def _key():
    t = ast.parse(open(LIVE).read())
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", None) == "KEY" for x in n.targets):
            return n.value.value
KEY = _key()
URL = f"https://mainnet.helius-rpc.com/?api-key={KEY}"
PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
PUMPSWAP = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
OUR = "4g49xGbgHZk3QYR1o6QSfDUbHmJZFwN6iDp6Vco1skff"
WSOL = "So11111111111111111111111111111111111111112"
JITO = {"96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5","HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
        "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY","ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
        "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh","ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
        "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL","3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"}
_lock = threading.Lock(); _last = [0.0]
MIN_GAP = 0.25  # <= 4 req/s overall
def _throttle():
    with _lock:
        now = time.time(); w = _last[0] + MIN_GAP - now
        if w > 0: time.sleep(w)
        _last[0] = time.time()
def _redact(s): return str(s).replace(KEY, "<key>")
def rpc(method, params, cache=True):
    h = hashlib.sha1(json.dumps([method, params]).encode()).hexdigest()
    p = os.path.join(CACHE, "rpc_" + h + ".json")
    if cache and os.path.exists(p): return json.load(open(p))
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for i in range(5):
        try:
            _throttle()
            req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r: j = json.load(r)
            if "error" in j:
                e = str(j["error"])
                if "not available" in e or "skipped" in e.lower(): res = None; break
                raise RuntimeError(_redact(e))
            res = j["result"]; break
        except Exception as e:
            if i == 4: raise RuntimeError(_redact(e)) from None
            time.sleep(1.5 * (i + 1))
    if cache and res is not None: json.dump(res, open(p, "w"))
    return res
def enhanced(addr, before=None, limit=100, cache=True):
    tag = f"enh_{addr}_{before or 'head'}_{limit}"
    p = os.path.join(CACHE, tag + ".json")
    if cache and before and os.path.exists(p): return json.load(open(p))
    url = f"https://api.helius.xyz/v0/addresses/{addr}/transactions?api-key={KEY}&limit={limit}"
    if before: url += f"&before={before}"
    for i in range(5):
        try:
            _throttle()
            with urllib.request.urlopen(urllib.request.Request(url), timeout=90) as r: j = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if i == 4: raise RuntimeError(f"HTTP {e.code}") from None
            time.sleep(2 * (i + 1))
        except Exception as e:
            if i == 4: raise RuntimeError(_redact(e)) from None
            time.sleep(2 * (i + 1))
    if cache: json.dump(j, open(p, "w"))
    return j
A58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58d(d):
    n = 0
    for c in d: n = n * 58 + A58.index(c)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\x00" * (len(d) - len(d.lstrip("1"))) + raw
def b58e(b):
    n = int.from_bytes(b, "big"); s = ""
    while n: n, r = divmod(n, 58); s = A58[r] + s
    return "1" * (len(b) - len(b.lstrip(b"\x00"))) + s
# --- PDA derivation (ed25519 off-curve check)
import hashlib as _h
_P = 2**255 - 19; _D = (-121665 * pow(121666, _P - 2, _P)) % _P
def on_curve(b):
    y = int.from_bytes(b, "little") & ((1 << 255) - 1)
    if y >= _P: return False
    y2 = y * y % _P; u = (y2 - 1) % _P; v = (_D * y2 + 1) % _P
    x2 = u * pow(v, _P - 2, _P) % _P
    return x2 == 0 or pow(x2, (_P - 1) // 2, _P) == 1
def find_pda(seeds, program):
    pid = b58d(program)
    for bump in range(255, -1, -1):
        h = _h.sha256(b"".join(seeds) + bytes([bump]) + pid + b"ProgramDerivedAddress").digest()
        if not on_curve(h): return b58e(h)
_curve_cache = {}
def bonding_curve(mint):
    if mint not in _curve_cache: _curve_cache[mint] = find_pda([b"bonding-curve", b58d(mint)], PUMP)
    return _curve_cache[mint]
