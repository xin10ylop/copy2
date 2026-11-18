# The pre-alert crew, pre-registered Nov 18 ~02:00 UTC, before any price path of these coins is read

`out/c1_crew.txt`: on 15,730 coins the VIP-map wallets bought inside the VIP exports' spans, the share the SolHouse VIP
alerted next rises with the number of crew wallets buying within 120 s: 1 → 7.8%, 2 → 13.4%, 3 → 18.8%, 4 → 27.1%,
5 → 36.0%. The alert comes ~80 s after the first crew buy; the 2nd crew buy ~2-5 s after the first.

**The trade:** trigger on the k-th distinct crew wallet's first buy of a coin within 120 s of the first crew buy; enter
at the first curve trade in a later slot, 0.5 SOL, any price. Exit: if the VIP alerts the coin before the cap, sell at
the first trade d s after the alert; else at the first trade `cap` s after the first crew buy. A completed curve sells
at its last curve trade. 0.0345 SOL a round trip.
**Grid (picked on export 1, Oct 31 - Nov 6 UTC):** k in {2, 3, 4}; d in {0, 15, 30}; cap in {90, 120, 180}.
**Scored once on export 2 (Nov 9 - 17 UTC)** with the one setting picked. **Pass:** positive; positive without the best
2%; bootstrap P(mean > 0) 95%+; 40+ trades.

**Narrowed before any path is read (Nov 18 ~02:05 UTC):** k in {3, 4} only (k=2 means about 4,000 coins to fetch); each path the first 300 s after the first crew buy (every exit falls by then: cap 180 s + d 30 s).
