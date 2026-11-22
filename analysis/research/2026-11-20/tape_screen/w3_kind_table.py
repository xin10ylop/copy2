# CqCAzte8 (Nov 22): tp 3x / 420 s / stall 240 by coin kind on the 3 blind blocks, copies and SOL per block (w3_robust.py up to its pick)
src = open("/home/user/copy2/analysis/research/2026-11-20/tape_screen/w3_robust.py").read()
src = src.split("real = rolling(G)")[0] + '''
E = ENAMES.index("tp 3x / 420 s / stall 240")
for kd in ("token", "SOL", "all"):
    V, keep = value((kd, 0.5)); cells = []; tot = []
    for b in (1, 2, 3):
        v = V[blocks[b]][keep[blocks[b]], E]; tot.append(v); cells.append(f"{len(v):3d} copies {v.sum():+6.2f} SOL ({100 * v.mean():+5.1f}%)")
    a = np.concatenate(tot); k = max(1, round(0.02 * len(a)))
    print(f"{kd:5s} | " + " | ".join(cells) + f" | ALL {len(a)} copies {a.sum():+6.2f} SOL ({100 * a.mean():+5.1f}%), without its best {k}: {a.sum() - np.sort(a)[-k:].sum():+6.2f} SOL")
'''
exec(compile(src, "tbl2", "exec"), {"__file__": "/home/user/copy2/analysis/research/2026-11-20/tape_screen/w3_robust.py", "__name__": "__main__"})
