# The own-history check alone (Nov 22): w2_grid.py part 1 (its own result by day, Helius history, MAXPAGES caps it),
# no coin replays: about 100 credits a 1,000 transactions.  HELIUS_URL=... RPC_URL=... MAXPAGES=10 python3 -I own_only.py SP WALLET
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [os.path.join(HERE, "w2_grid.py"), sys.argv[1], sys.argv[2], "0", "0", "14"]
src = open(sys.argv[0]).read().split("# 2-3. the grid")[0]
__file__ = sys.argv[0]; exec(compile(src, sys.argv[0], "exec"))
print("OWN PASS")
