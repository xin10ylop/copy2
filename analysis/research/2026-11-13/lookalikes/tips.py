# tip_accounts.json for rivalpnl/pumpparse.py (it only labels tips in each row; nothing here scores on it): the 8 Jito
# tip accounts, and every account wallet 4 paid exactly 1,067,000 or 1,010,000 lamports to in since_stop/w4tx
# (its tip sizes, ../../2026-11-12/siblings/README.md).   python3 -I tips.py SPD OUT.json
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import b58d
SPD, OUT = sys.argv[1], sys.argv[2]; SYS = "11111111111111111111111111111111"
JITO = ["96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5", "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe", "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
        "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49", "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh", "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
        "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL", "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"]
tips = {a: "jito" for a in JITO}
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["transaction"]["message"]; ks = m["accountKeys"]
    for ix in m["instructions"]:
        if ix["programIdIndex"] >= len(ks) or ks[ix["programIdIndex"]] != SYS: continue
        d = b58d(ix.get("data", "") or "1")
        if len(d) == 12 and d[:4] == b"\x02\x00\x00\x00" and int.from_bytes(d[4:], "little") in (1067000, 1010000):
            tips.setdefault(ks[ix["accounts"][1]], "w4tip")
json.dump(tips, open(OUT, "w")); print(len(tips), "tip accounts")
