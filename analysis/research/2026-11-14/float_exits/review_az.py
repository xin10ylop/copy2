# The A-to-Z review the owner asked for (Nov 14): every exit setting over all the data (Oct 21 18:30 UTC to now; the
# unseen week A, the study halves B and C, and what came after), 2 open (SOL 1, WBTC 2, PUMP 1, SPCX 1), raw model.
# For each timer x take profit (his early sale followed at 30-290 s under 1.5x): the net by block, without each
# block's best 5, the deepest fall, and how often a copy WINS (any exit above zero), wins big (+50% of the stake or
# more), and reaches the take profit, a day (landing 4).
#   python3 -I review_az.py SPD [STAKE]
import sys, os, datetime, collections
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
STAKE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + [str(STAKE)]; import float_exits as F
import lib as L
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
days = (F.END - T0) / 86400
def line(tp, hold, early=(30, 290, 1.5), sl=None, tag=""):
    kw = dict(tp=tp, hold=hold, early=early, sl=sl); full = [F.sim(F.rows, n, kw, stake=STAKE, caps=CAPS) for n in L.LAND]
    cells = []; w5 = 0
    for b in range(3):
        v = [sorted((x[1] for x in res if blk(x[0]) == b), reverse=True) for res in full]
        cells.append(sum(sum(x) for x in v) / 3); w5 += sum(sum(x[5:]) for x in v) / 3
    res = full[0]; live = [x for x in res if x[2] != "refused"]; dd = worst = 0.0
    for r, net, why in res:
        dd = min(0.0, dd + net); worst = min(worst, dd)
    win = sum(1 for x in live if x[1] > 0); big = sum(1 for x in live if x[1] >= 0.5 * STAKE); tpn = sum(1 for x in live if x[2] == "tp")
    print(f"   tp {str(tp):4s} {hold:>4} s {tag:14s} | {cells[0]:+6.2f} {cells[1]:+6.2f} {cells[2]:+6.2f} | {sum(cells):+6.2f} | {w5:+6.2f}     | {worst:+5.2f}  | "
          f"{len(live) / days:4.1f} | {win / days:4.1f} ({100 * win / len(live):2.0f}%) | {big / days:3.1f}     | {tpn / days:3.1f} | {sum(x[1] for x in live if x[1] > 0) / max(1, win):+.2f} / {sum(x[1] for x in live if x[1] <= 0) / max(1, len(live) - win):+.2f}")
if __name__ == "__main__":
    f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
    print(f"{len(F.rows)} copyable buys, {f(T0)} to {f(F.END)} Beirut ({days:.1f} days); stake {STAKE} SOL")
    print(f"   {'rule (early 30-290)':30s} | A      B      C      | all    | w/o best 5 | fall   | copies, wins a day (rate), big wins, take profits a day | average win / loss, SOL")
    for hold in (300, 450, 600, 750, 900, 1200, 1790):
        for tp in (2.0, 2.4, 3.0, 4.0):
            line(tp, hold, tag="<- live" if (tp, hold) == (3.0, 1200) else "")
        print()
    print("other choices at tp 3.0, 600 s:")
    line(3.0, 600, early=None, tag="never follow"); line(3.0, 600, early=(30, 180, 1.5), tag="early 30-180"); line(3.0, 600, early=(30, 330, 1.5), tag="early 30-330")
    line(3.0, 600, early=(0, 1e9, 1e9), tag="every sale"); line(3.0, 600, sl=0.5, tag="stop 0.5x"); line(3.0, 600, sl=0.7, tag="stop 0.7x")
