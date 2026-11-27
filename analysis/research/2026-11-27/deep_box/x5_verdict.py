# One candidate's verdict from its deep-test files (Nov 27; the owner: "pick wallets carefully, but that doesnt mean dont pick,
# that means knowing what to pick"). The rules, written before any of these candidates was tested, after www and fff:
#   R1 the standard exit (tp 3x / 420 s / stall 240, all its coins of 0.5+ SOL) over its 14 days: over +3% a copy, positive
#      without its best 2% of copies, positive in at least 3 of its 4 time blocks
#   R3 at least 40 copies in the 14 days (blocks of 10)
# PASS = R1 and R3. The worst block is reported, not used: checked on the wallets we know (Nov 27), a -10% floor would have
# cut www (-11.0%) and fff (-10.9%), which lost live, and iii (Bing35WC, -10.7% in its Nov 25 test), our best live unit: it
# does not tell them apart. What guards against a wallet like www is the stake and a stop fixed before it starts: a PASS
# starts at 0.25 SOL, daily stop 0.5, and is stopped at -1.0 SOL in all or if negative after 20 trades. Reported beside it:
# the blind rolling pick (w3_robust), the wallet's own result, and the exit and rule search (x2 / x4), which set its exit.
#   python3 -I x5_verdict.py OUTDIR WALLET8
import sys, re
D, W8 = sys.argv[1], sys.argv[2]
rd = lambda f: open(f"{D}/{f}").read() if __import__("os").path.exists(f"{D}/{f}") else ""
setup, robust, x2, x4 = rd(f"{W8}_setup.txt"), rd(f"{W8}_all.txt"), rd(f"{W8}_x2.txt"), rd(f"{W8}_x4.txt")
num = lambda s: float(s.replace("%", "")) if s not in ("-", "") else None
m = re.search(r"^all\s+0\.5\+ SOL tp 3x / 420 s / stall 240\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)% \(\s*(\d+)\)\s+(\S+)\s+(\d)/4", setup, re.M)
own = re.search(r"own result ([+-][\d.]+) SOL over (\d+) days, up on (\d+)", setup or robust)
res = re.search(r"^RESULT: (.*)$", robust, re.M)
v2 = re.search(r"VERDICT: (.*)", x2); v4 = re.search(r"VERDICT: (.*)", x4)
if not m:
    print(f"{W8}: NO DATA (the setup table is missing: {'history fetch failed?' if not setup else 'no 0.5+ SOL copies'})"); sys.exit()
blocks = [num(x) for x in m.groups()[:4]]; allp, n, wo2, nplus = num(m.group(5)), int(m.group(6)), float(m.group(7)), int(m.group(8))
worst = min(b for b in blocks if b is not None)
r1 = allp > 3 and wo2 > 0 and nplus >= 3; r3 = n >= 40
ok = r1 and r3
print(f"{W8}: {'PASS' if ok else 'FAIL'}  standard exit {allp:+.1f}% a copy on {n}, blocks " + " / ".join("-" if b is None else f"{b:+.1f}" for b in blocks)
      + f", w/o best 2% {wo2:+.2f} SOL at 1 SOL, {nplus}/4 positive")
print(f"    R1 (>+3%, w/o 2% > 0, 3+ blocks) {'yes' if r1 else 'NO'} | R3 (40+ copies) {'yes' if r3 else 'NO'} | worst block {worst:+.1f}%")
print(f"    own {own.group(1)} SOL over {own.group(2)} days, up on {own.group(3)} | blind rolling pick: {res.group(1) if res else '?'}")
print(f"    exit search: {v2.group(1).strip() if v2 else '?'}")
print(f"    rule search: {v4.group(1).strip() if v4 else '?'}")
