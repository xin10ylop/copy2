# calls.team's public caller pages (Nov 18, the owner: "go deep on calls.team"): each caller page lists its latest 50
# calls (no pagination) with the exact time (data-ts) and the full mint (in the trade links). A handful of pages, read
# for reference with a pause between them (the site allows use=reference). Out: SP/ct/calls.json
#   python3 -I ct1_fetch_calls.py SP caller1 caller2 ...
import sys, re, json, time, html, subprocess, os
SP, CALLERS = sys.argv[1], sys.argv[2:]; out = []
for c in CALLERS:
    page = subprocess.run(["curl", "-sS", "-L", "-m", "30", "-A", "Mozilla/5.0", f"https://calls.team/callers/{c}/"], capture_output=True, text=True).stdout
    n = 0
    for row in re.findall(r"<tr>(.*?)</tr>", page, flags=re.S):
        ts = re.search(r'data-ts="([\d.]+)"', row); mint = re.search(r'gmgn\.ai/sol/token/(?:[A-Za-z0-9]+_)?([1-9A-HJ-NP-Za-km-z]{32,44})', row)
        order = re.search(r'<td class="num">#(\d+)</td>', row); sym = re.search(r"<b>([^<]*)</b>", row)
        if ts and mint: out.append(dict(caller=c, t=float(ts.group(1)), mint=mint.group(1), order=int(order.group(1)) if order else None, sym=html.unescape(sym.group(1)) if sym else "")); n += 1
    print(c, n, "calls"); time.sleep(2)
os.makedirs(f"{SP}/ct", exist_ok=True); json.dump(out, open(f"{SP}/ct/calls.json", "w")); print(len(out), "calls,", len({x['mint'] for x in out}), "coins")
