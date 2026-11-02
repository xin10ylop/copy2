# Shared helper for w4rev: the scan agent's Triton client and pump event decoders (../agents/scan/bin/crc.py: URL read
# from the old scratchpad's month/.triton_url, never printed, redacted in errors), with this study's own cache, plus the
# canonical PumpSwap pool derivation (seeds as crates/pump-codec/src/pda.rs; the ed25519 off-curve check of
# rivalpnl/common.py).
import os, sys, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "agents", "scan", "bin"))
import crc                                   # noqa: E402
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
crc.CACHE = os.path.join(HERE, "cache"); os.makedirs(crc.CACHE, exist_ok=True)
crc.OUT = OUT
rpc, tx, sigs, events, keys_of, jdump, red = crc.rpc, crc.tx, crc.sigs, crc.events, crc.keys_of, crc.jdump, crc.red
b58d, b58e = crc.b58d, crc.b58e
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
H9 = SP0 + "/h9long"
PUMP, PAMM, MINT_AUTH = crc.PUMP, crc.PUMPSWAP, crc.MINT_AUTH
WSOL = crc.WSOL; WBTC = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"; SOL_LIKE = crc.SOL_LIKE
W4 = crc.W4
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
        h = hashlib.sha256(b"".join(seeds) + bytes([bump]) + pid + b"ProgramDerivedAddress").digest()
        if not on_curve(h): return b58e(h)
def pool_authority(m): return find_pda([b"pool-authority", b58d(m)], PUMP)
def canonical(m, q): return find_pda([b"pool", (0).to_bytes(2, "little"), b58d(pool_authority(m)), b58d(m), b58d(q)], PAMM)
def bonding_curve(m): return find_pda([b"bonding-curve", b58d(m)], PUMP)
assert canonical("2gLnaQN8Y73Qc62gMmX6WtJQjFnbvE7vgzUJ37WJpump", WSOL) == "8Xev4PoVsLfyt1A31cGUcGU9tW738MaGsB2MczezcgVf"
def jl(p): return json.load(open(p))
# Disk is short (the volume filled on Nov 1 ~23:50 UTC with the raw-response cache): no caching of transactions or
# signature pages from here on; the decoded rows (out/*.json, out/tapes/) are the record.
def tx(sig): return crc.rpc("getTransaction", [sig, crc.TXO], cache=False)
def sigs(addr, before=None, until=None, limit=1000, cache=False): return crc.sigs(addr, before=before, until=until, limit=limit, cache=False)
