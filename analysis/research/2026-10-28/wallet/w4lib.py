# Helpers for the wallet-4 check: transaction parsing (system and SPL transfers with counterparties), row loading.
import sys, json, struct, time
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
OUT = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet"
sys.path.insert(0, SP + "/month"); import tri
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
SYS = "11111111111111111111111111111111"; CB = "ComputeBudget111111111111111111111111111111"
TOK = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"; T22 = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
WSOL = "So11111111111111111111111111111111111111112"; PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
PUMPSWAP = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"; JUP = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
A58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58d(d):
    n = 0
    for c in d: n = n * 58 + A58.index(c)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\x00" * (len(d) - len(d.lstrip("1"))) + raw
TIPS = json.load(open(SP + "/rivalpnl/tip_accounts.json"))
def ts(bt): return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(bt)) if bt else "?"
def tsb(bt): return time.strftime("%m-%d %H:%M", time.gmtime(bt + 7200)) if bt else "?"  # Beirut = UTC+2
def keys_of(tx):
    m = tx["transaction"]["message"]; ks = [k["pubkey"] if isinstance(k, dict) else k for k in m["accountKeys"]]
    la = (tx.get("meta") or {}).get("loadedAddresses") or {}
    return ks + la.get("writable", []) + la.get("readonly", [])
def ixs(tx):
    ks = keys_of(tx); m = tx["transaction"]["message"]; meta = tx.get("meta") or {}
    for ix in m["instructions"]:
        yield ks[ix["programIdIndex"]], [ks[a] for a in ix.get("accounts", [])], b58d(ix.get("data", "")), False
    for grp in meta.get("innerInstructions") or []:
        for ix in grp["instructions"]:
            yield ks[ix["programIdIndex"]], [ks[a] for a in ix.get("accounts", [])], b58d(ix.get("data", "")), True
def u64(b, o): return struct.unpack_from("<Q", b, o)[0]
def tok_owner_map(tx):
    """token account -> (owner, mint), from pre/post token balances"""
    ks = keys_of(tx); meta = tx.get("meta") or {}; mp = {}
    for side in ("preTokenBalances", "postTokenBalances"):
        for b in meta.get(side) or []:
            mp[ks[b["accountIndex"]]] = (b.get("owner"), b.get("mint"), b["uiTokenAmount"].get("decimals", 0))
    return mp
def transfers(tx):
    """list of (kind, src_owner, dst_owner, amount_raw, mint, decimals, inner). kind sys|create|spl. SOL in lamports."""
    out = []; om = tok_owner_map(tx)
    for prog, accs, data, inner in ixs(tx):
        if prog == SYS and len(data) >= 4:
            k = struct.unpack_from("<I", data, 0)[0]
            ow = lambda a: om[a][0] if a in om and om[a][0] else a   # a wSOL/token account counts as its owner
            if k == 2 and len(data) >= 12 and len(accs) >= 2: out.append(("sys", ow(accs[0]), ow(accs[1]), u64(data, 4), "SOL", 9, inner))
            elif k == 0 and len(data) >= 12 and len(accs) >= 2: out.append(("create", ow(accs[0]), ow(accs[1]), u64(data, 4), "SOL", 9, inner))
            elif k == 11 and len(accs) >= 3 and len(data) >= 12: out.append(("sys", ow(accs[0]), ow(accs[2]), u64(data, 4), "SOL", 9, inner))
        elif prog in (TOK, T22) and data:
            k = data[0]
            if k == 3 and len(accs) >= 3 and len(data) >= 9:
                s, d = accs[0], accs[1]; so = om.get(s, (s, None, 0)); do = om.get(d, (d, None, 0))
                mint = so[1] or do[1]; out.append(("spl", so[0], do[0], u64(data, 1), mint, so[2] or do[2], inner))
            elif k == 12 and len(accs) >= 4 and len(data) >= 10:
                s, mint, d = accs[0], accs[1], accs[2]; so = om.get(s, (s, mint, data[9])); do = om.get(d, (d, mint, data[9]))
                out.append(("spl", so[0], do[0], u64(data, 1), mint, data[9], inner))
    return out
def sol_delta(tx, addr):
    ks = keys_of(tx); meta = tx["meta"]
    if addr not in ks: return 0
    i = ks.index(addr); return meta["postBalances"][i] - meta["preBalances"][i]
def progs_of(tx):
    return sorted({p for p, *_ in ixs(tx)} - {SYS, CB})
def rows():
    return [json.loads(l) for l in open(SP + "/h9long/H9kuqGKN.jsonl")]
def oldsigs():
    return [x for l in open(OUT + "/w4_oldsigs.jsonl") for x in json.loads(l)]
