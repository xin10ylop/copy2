# Shared helpers for group G1. Chain calls go through rescore2.rpc (paced, Triton URL read by rescore2 itself).
import sys, json, os, base64
GO = "/tmp/claude-0/-home-user/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/gmgn-out"
G1 = os.path.dirname(os.path.abspath(__file__))     # the final pass: its own folder
sys.path.insert(0, GO)
import rescore2 as R
WSOL = R.WSOL
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def b58dec(s):
    n = 0
    for ch in s: n = n * 58 + B58.index(ch)
    out = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + out

def keys_of(tx):
    tr = tx["transaction"]; raw = tr.get("accountKeys") or tr.get("message", {}).get("accountKeys") or []
    keys = [k["pubkey"] if isinstance(k, dict) else k for k in raw]
    if tx["meta"].get("loadedAddresses"):
        keys += tx["meta"]["loadedAddresses"].get("writable", []) + tx["meta"]["loadedAddresses"].get("readonly", [])
    return keys

def deltas(tx, owner, mint):
    """(coin change, quote change, quote mint) for owner; copied from stage3.deltas (SOL fee added back for the payer)."""
    meta = tx["meta"]; keys = keys_of(tx); ch = {}
    for side, sign in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            if b.get("owner") != owner: continue
            ch[b["mint"]] = ch.get(b["mint"], 0.0) + sign * float(b["uiTokenAmount"]["uiAmount"] or 0)
    dt = ch.pop(mint, 0.0)
    if owner in keys:
        i = keys.index(owner); sol = (meta["postBalances"][i] - meta["preBalances"][i] + (meta["fee"] if i == 0 else 0)) / 1e9
        ch[WSOL] = ch.get(WSOL, 0.0) + sol
    q = max(((k, v) for k, v in ch.items() if v * dt < 0), key=lambda kv: abs(kv[1]), default=(None, 0.0))
    return dt, q[1], q[0]

def sol_change(tx, owner):
    """owner's native SOL + wSOL change in the tx, fee excluded (what the trade itself moved)."""
    meta = tx["meta"]; keys = keys_of(tx); s = 0.0
    if owner in keys:
        i = keys.index(owner); s += (meta["postBalances"][i] - meta["preBalances"][i] + (meta["fee"] if i == 0 else 0)) / 1e9
    for side, sign in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            if b.get("owner") == owner and b["mint"] == WSOL: s += sign * float(b["uiTokenAmount"]["uiAmount"] or 0)
    return s

SYS = "11111111111111111111111111111111"
CB = "ComputeBudget111111111111111111111111111111"
def fee_tip(tx, owner):
    """(fee SOL, priority SOL (fee - 5000/sig), [(dest, SOL)] top-level system transfers from owner to non-token accounts
    = tips or platform fees, compute-unit price (micro-lamports) if set, CU limit, uses a durable nonce first)."""
    meta = tx["meta"]; keys = keys_of(tx); msg = tx["transaction"]["message"]
    nsig = len(tx["transaction"].get("signatures") or [1])
    tokacc = {keys[b["accountIndex"]] for side in ("preTokenBalances", "postTokenBalances") for b in (meta.get(side) or [])}
    tips, cup, cul, nonce = [], None, None, False
    for j, ins in enumerate(msg.get("instructions") or []):
        prog = keys[ins["programIdIndex"]]; data = b58dec(ins.get("data") or "")
        if prog == SYS and len(data) >= 12 and int.from_bytes(data[:4], "little") == 2:
            src, dst = keys[ins["accounts"][0]], keys[ins["accounts"][1]]
            if src == owner and dst not in tokacc: tips.append((dst, int.from_bytes(data[4:12], "little") / 1e9))
        if prog == SYS and j == 0 and len(data) >= 4 and int.from_bytes(data[:4], "little") == 4: nonce = True
        if prog == CB and data:
            if data[0] == 3 and len(data) >= 9: cup = int.from_bytes(data[1:9], "little")
            if data[0] == 2 and len(data) >= 5: cul = int.from_bytes(data[1:5], "little")
    fee = meta["fee"] / 1e9
    return fee, fee - 5000 * nsig / 1e9, tips, cup, cul, nonce

def programs(tx):
    keys = keys_of(tx); msg = tx["transaction"]["message"]
    out = [keys[i["programIdIndex"]] for i in msg.get("instructions") or []]
    for g in tx["meta"].get("innerInstructions") or []:
        out += [keys[i["programIdIndex"]] for i in g["instructions"]]
    return out

VENUES = {"6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "pump curve", "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "PumpSwap",
          "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium v4", "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM",
          "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM", "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Raydium LaunchLab",
          "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo": "Meteora DLMM", "cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG": "Meteora DAMM v2",
          "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora DAMM v1", "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "Meteora DBC",
          "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca", "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter",
          "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ": "pump fees", "FLASHX8DrLbgeR8FcfNV1F5krxYcYMUdBkrP1EPBtxB9": "Axiom router",
          "boop8hVGQGqehUK2iVEMEnMrL5RbjywRzHKBmBE7ry4": "Boop", "MoonCVVNZFSYkqNXP6bxHLPL6QQJiMagDL3qcqUQTrG": "Moonshot"}
def venue(tx):
    ps = programs(tx); return sorted({VENUES[p] for p in ps if p in VENUES and VENUES[p] not in ("pump fees",)})

def block_pos(slot, sig, mint):
    """(its index in the block (all txs, failed included), txs in the block, coin trades ahead of it in the block)."""
    b = R.rpc("getBlock", [slot, {"encoding": "json", "transactionDetails": "signatures", "rewards": False, "maxSupportedTransactionVersion": 1}])
    if not b: return None
    sigs = b.get("signatures") or []
    idx = sigs.index(sig) if sig in sigs else None
    ahead = None
    tr = R.trades_in(slot, mint)
    for n, (sg, ss, p) in enumerate(tr):
        if sig in ss: ahead = n; break
    return idx, len(sigs), ahead

def jl(path):
    return json.load(open(path))
