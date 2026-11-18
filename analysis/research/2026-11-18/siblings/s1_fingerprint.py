# Wallet 4's siblings (Nov 18, the owner: "having several wallet 4's can multiply everything"). Step 1: wallet 4's
# transaction fingerprint now (07-rework-2026-10-28/wallet-check.md §7 had: durable nonce, 1,067,000 / 1,010,000-lamport
# tips, about 1.5 SOL other-token buys at create+0/+1). Its newest buy transactions: the first instruction (a durable
# nonce advance or not), the compute budget (unit limit, unit price), SOL transfers (tips: amount and recipient), the
# programs called, the version and lookup tables, the signers.
#   RPC_URL=... LK=SP/sib/lk python3 -I s1_fingerprint.py SP [N=150]   -> out/s1_fingerprint.txt
import sys, os, json, glob, collections
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib
SP = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 150; W4 = lib.W4
CB = "ComputeBudget111111111111111111111111111111"; SYS = "11111111111111111111111111111111"
def fp(t):
    msg = t["transaction"]["message"]; ix = msg["instructions"]; f = {}
    f["nonce"] = bool(ix) and ix[0].get("programId") == SYS and isinstance(ix[0].get("parsed"), dict) and ix[0]["parsed"].get("type") == "advanceNonce"
    f["cu_limit"] = f["cu_price"] = None; f["tips"] = []
    for i in ix:
        p = i.get("programId")
        if p == CB and i.get("data"):
            raw = lib.b58d(i["data"])
            if raw[:1] == b"\x02": f["cu_limit"] = int.from_bytes(raw[1:5], "little")
            if raw[:1] == b"\x03": f["cu_price"] = int.from_bytes(raw[1:9], "little")
        if p == SYS and isinstance(i.get("parsed"), dict) and i["parsed"].get("type") == "transfer":
            f["tips"].append((i["parsed"]["info"]["lamports"], i["parsed"]["info"]["destination"]))
    f["progs"] = tuple(sorted({i.get("programId") for i in ix}))
    f["version"] = t.get("version"); f["alts"] = len(msg.get("addressTableLookups") or []); f["signers"] = len(t["transaction"]["signatures"])
    f["n_ix"] = len(ix); f["fee"] = t["meta"]["fee"]
    return f
if __name__ == "__main__":
    h = json.load(open(glob.glob(f"{SP}/winners/hist/H9kuqGKN*.json")[0])); buys = sorted((e for e in h["trades"] if e["buy"]), key=lambda e: -e["t"])
    sigs = []; before = None
    while len(sigs) < N * 3:
        s = lib.sigs(W4, before=before, limit=1000, cache=False)
        if not s: break
        sigs += [x["signature"] for x in s if x.get("err") is None]; before = s[-1]["signature"]
    F = []
    for sg in sigs:
        t = lib.tx(sg)
        if not t or not any(k == "trade" and e.get("is_buy") and e.get("user") == W4 for k, e in lib.events(t)): continue
        F.append(fp(t))
        if len(F) >= N: break
    print(f"wallet 4: {len(F)} of its newest buy transactions")
    print("durable nonce first:", collections.Counter(f["nonce"] for f in F))
    print("unit limit:", collections.Counter(f["cu_limit"] for f in F).most_common(5))
    print("unit price:", collections.Counter(f["cu_price"] for f in F).most_common(5))
    print("tip amounts:", collections.Counter(a for f in F for a, _ in f["tips"]).most_common(8))
    print("tip recipients:", len({d for f in F for _, d in f["tips"]}), collections.Counter(d[:8] for f in F for _, d in f["tips"]).most_common(5))
    print("transfers per tx:", collections.Counter(len(f["tips"]) for f in F))
    print("programs:", collections.Counter(tuple(p[:6] for p in f["progs"]) for f in F).most_common(4))
    print("version / lookup tables / signers / instructions:", collections.Counter((f["version"], f["alts"], f["signers"], f["n_ix"]) for f in F).most_common(5))
    print("fee:", collections.Counter(f["fee"] for f in F).most_common(4))
    json.dump(F, open(f"{SP}/sib_w4_fp.json", "w"), default=list)
