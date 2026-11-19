# Is the fetched trade data complete? For coins the leaders bought, rebuild the curve's state from our logs and compare
# with the curve's own reserves on chain now (only coins with no trade in the last 2 days, not graduated).
import sys, json, random, urllib.request
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-19/rh_deep"); import rhd_lib as R
from Crypto.Hash import keccak
D = sys.argv[1]; DATA = R.Data(D); RPC = "https://rpc.mainnet.chain.robinhood.com"
def sel(s): k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def call(to, d):
    r = urllib.request.Request(RPC, json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": to, "data": d}, "latest"]}).encode(), {"content-type": "application/json", "user-agent": "curl/8"})
    return int(json.load(urllib.request.urlopen(r, timeout=20))["result"], 16)
LEAD = {"0x9a3955a122ab8a649a8511df2dce169471fd0ec1", "0x5bc235acecff3dde394f4bfc696f7c35efd502f0", "0xc54d3914f91f984d61b63d491f38934c4e706b79"}
cands = [c for c in DATA.L if c in DATA.TR and any(x[3] in LEAD and x[2] for x in DATA.TR[c]) and c not in DATA.GRAD and DATA.L[c] not in DATA.GRAD]
random.seed(1); random.shuffle(cands); n = bad = 0
for c in cands:
    tr = DATA.path(c)
    if not tr or tr[-1]["t"] > DATA.t_end - 2 * 86400: continue
    try: vt_chain = call(c, sel("tokenReserve()")) / 1e18; vq_chain = call(c, sel("quoteReserve()")) / 1e18
    except Exception as e: print(c, "call failed", e); continue
    vt_m, vq_m = tr[-1]["vt"], tr[-1]["vq"] / 1e9
    d = abs(vt_chain - vt_m) / vt_chain; n += 1; bad += d > 0.001
    print(f"{c[:10]} trades {len(tr):5d}  tokens: chain {vt_chain:14.1f} ours {vt_m:14.1f} ({100*d:6.3f}%)  quote: chain {vq_chain:.5f} ours {vq_m:.5f}")
    if n >= 30: break
print(f"{n} coins checked, {bad} differ by more than 0.1%")
