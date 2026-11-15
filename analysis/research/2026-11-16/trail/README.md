# A trailing stop (Nov 15 evening)

The owner, watching #36 `GGSWz3uu` peak at 2.56x and fall to 1.42x: "manually I would have sold it by now".
`trail.py`: once the price reached `a` times our buy, sell when it is `d` under its high since our buy; on top of the
live rule and with tp 4.0 / none; 1,238 buys (seven kinds, 1.3+ SOL, every fee tier, Oct 21 - Nov 15 13:04 UTC),
0.5 SOL, 2 open, mean of three landings.

    python3 -I trail.py CQ ALL > out/trail.txt

- **With tp 3.0 and 600 s, every trail of 10-30% loses money:** live +56.63; 20% once 1.5x +32.53, 30% once 2.0x
  +50.70, 25% once 2.5x +50.90. The coins that reach 3x often dip 20-40% first.
- 40-70% (`../signals/out/signals2.txt`) are within ±0.5 SOL of live: no gain.
- Picked on two blocks and scored on the third: −0.82 SOL. Nothing here.
