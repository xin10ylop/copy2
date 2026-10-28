# Pump bonding-curve PDA (same derivation as rivalpnl/common.py, without importing it).
import hashlib
_P = 2**255 - 19; _D = (-121665 * pow(121666, _P - 2, _P)) % _P
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
def on_curve(b):
    y = int.from_bytes(b, "little") & ((1 << 255) - 1)
    if y >= _P: return False
    y2 = y * y % _P; u = (y2 - 1) % _P; v = (_D * y2 + 1) % _P
    x2 = u * pow(v, _P - 2, _P) % _P
    return x2 == 0 or pow(x2, (_P - 1) // 2, _P) == 1
def pda(seeds, program):
    pid = b58d(program)
    for bump in range(255, -1, -1):
        h = hashlib.sha256(b"".join(seeds) + bytes([bump]) + pid + b"ProgramDerivedAddress").digest()
        if not on_curve(h): return b58e(h)
def bonding_curve(mint): return pda([b"bonding-curve", b58d(mint)], "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
