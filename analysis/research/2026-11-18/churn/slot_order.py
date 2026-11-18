# The in-slot order fix (Nov 18). The cached paths list the transactions inside one slot in no reliable order (seen on
# the ladder's launches: the second bundle listed before the first). The curve's reserves give the true order: a
# trade's state before it (vt + tok for a buy, vt - tok for a sale) is the state after the trade before it. reorder()
# chains each slot from the trade whose previous state is no other trade's state after; a slot that does not chain
# fully (a few in a thousand) keeps the listed order.
import collections
def _pre(e): return e["vt"] + e["tok"] if e["buy"] else e["vt"] - e["tok"]
def reorder(tr):
    out = []; i = 0; n = len(tr); fixed = 0
    while i < n:
        j = i
        while j < n and tr[j]["slot"] == tr[i]["slot"]: j += 1
        xs = tr[i:j]
        if len(xs) > 1:
            post = {e["vt"] for e in xs}; by = collections.defaultdict(list)
            for e in xs: by[_pre(e)].append(e)
            st = [e for e in xs if _pre(e) not in post]
            if len(st) == 1:
                seq = [st[0]]; used = {id(st[0])}
                while True:
                    nx = [e for e in by.get(seq[-1]["vt"], []) if id(e) not in used]
                    if not nx: break
                    seq.append(nx[0]); used.add(id(nx[0]))
                if len(seq) == len(xs):
                    fixed += seq != xs; xs = seq
        out += xs; i = j
    return out
def patch(ns):
    """Wrap a wallet_study / w5_copy namespace's cpath with the reorder."""
    cp = ns["cpath"]; ns["cpath"] = lambda *a, **k: reorder(cp(*a, **k)); return ns
