# The periods of this study (UTC), the same two weeks wallet 4 was last scored on (since_stop exit_search.py /
# vs_him_week.py): P1 = the pick week, Oct 29 12:02 -> Nov 5 06:49; P2 = the test week, Nov 5 06:49 -> Nov 12 06:49;
# P3 = the hours after, to the end of the fetch (reported, not used to pick or score).
PA, PB, PC = 1793275320, 1793861340, 1794466140
def per(t): return "P1" if t < PB else "P2" if t < PC else "P3"
