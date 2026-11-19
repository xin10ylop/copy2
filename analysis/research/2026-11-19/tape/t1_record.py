# The pump.fun tape (Nov 19; the owner: "this would cost too much, find another way ... how was wallet 4 found?").
# Wallet 4 was found on tapes the launch bot recorded from the live feed, not on fetched history. Fetching one day
# of history costs ~5.5 million transactions (~$57 at Triton's $10 a million calls + bandwidth); the live log stream
# of the pump program costs ~65 GB a day at $0.08 a GB (~$5). This records it: logsSubscribe (mentions pump,
# confirmed) on the Triton websocket; every successful transaction's CreateEvents and TradeEvents decoded from its
# "Program data:" lines; one JSON line per event, in arrival order (n = arrival number; the order inside a slot is the
# stream's, not proven to be the block's), hourly gz files OUT/tape_<YYYYmmddHH>.jsonl.gz; reconnects by itself; a
# stats line every minute (transactions, events, truncated logs, failed transactions skipped).
#   RPC_URL=<triton https url> python3 -I t1_record.py OUT
import sys, os, json, gzip, time, base64, asyncio
import websockets
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib
sys.path.insert(0, "/home/user/rugsnipe/analysis"); from rugsnipe_analysis import events as E
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
WS = "wss://" + os.environ["RPC_URL"].split("://", 1)[1]
KT = ("mint", "user", "is_buy", "sol", "tok", "vsol", "vtok", "rsol", "rtok", "fee_bps", "quote_mint", "quote_amount", "vquote", "ts")
KC = ("mint", "creator", "user", "quote_mint", "ts", "symbol")
st = dict(tx=0, ev=0, trunc=0, failed=0, n=0); fh = [None, None]
def out(row):
    h = time.strftime("%Y%m%d%H", time.gmtime())
    if fh[0] != h:
        if fh[1]: fh[1].close()
        fh[0], fh[1] = h, gzip.open(f"{OUT}/tape_{h}.jsonl.gz", "at")
    fh[1].write(json.dumps(row, separators=(",", ":")) + "\n")
async def run():
    async with websockets.connect(WS, max_size=None, open_timeout=20, ping_interval=20, ping_timeout=30) as ws:
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "logsSubscribe", "params": [{"mentions": [PUMP]}, {"commitment": "confirmed"}]}))
        last = time.time()
        while True:
            m = json.loads(await ws.recv()); r = m.get("params", {}).get("result")
            if not r: continue
            v = r["value"]
            if v.get("err"): st["failed"] += 1; continue
            st["tx"] += 1; slot = r["context"]["slot"]
            if any("Log truncated" in l for l in v["logs"]): st["trunc"] += 1
            for l in v["logs"]:
                if not l.startswith("Program data: "): continue
                try: raw = base64.b64decode(l[14:])
                except Exception: continue
                try:
                    if raw[:8] == E.DISC_TRADE: e = lib.decode_trade(raw[8:]); row = {"k": "t", **{k: e.get(k) for k in KT}}
                    elif raw[:8] == E.DISC_CREATE: e = lib.decode_create(raw[8:]); row = {"k": "c", **{k: e.get(k) for k in KC}}
                    else: continue
                except Exception: continue
                st["n"] += 1; st["ev"] += 1; out({"n": st["n"], "slot": slot, "sig": v["signature"], **row})
            if time.time() - last >= 60:
                fh[1] and fh[1].flush()
                print(f"{time.strftime('%H:%M:%S', time.gmtime())} tx {st['tx']} events {st['ev']} truncated {st['trunc']} failed skipped {st['failed']}", flush=True); last = time.time()
async def main():
    while True:
        try: await run()
        except Exception as x: print(f"{time.strftime('%H:%M:%S', time.gmtime())} reconnect after {type(x).__name__}", flush=True); await asyncio.sleep(3)
asyncio.run(main())
