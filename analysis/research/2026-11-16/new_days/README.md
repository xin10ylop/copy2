# The frozen setup on wallet 4's newest days (Nov 16)

The backtest data ended Nov 15 13:04 UTC. Here wallet 4's own buys from then to Nov 16 14:25 UTC (25.3 hours), never
used in any study: `fetch_w4.py` from Nov 15 12:00, the bot's scan with the seven floats at 1.3+ SOL, `build_rows.py`,
`model.py`'s paths (`NEW` = the scratchpad folder `newq`), then the live setup on them, 0.5 SOL.

    python3 -I new_days.py NEW CQ ALL > out/new_days.txt

**Result (`out/new_days.txt`):**

| | copies | a copy | median | won | reached 3x / 4x in 600 s |
|---|---|---|---|---|---|
| the backtest, Oct 21 - Nov 15 13:04 | 1,163 | +13.6% | −7.1% | 34% | 11.6% / 6.8% |
| the backtest's last 5 days | 154 | +26.9% | −7.2% | 39% | 17.5% / 10.4% |
| **new: Nov 15 13:04 - Nov 16 14:25** | **32** | **+11.0%** | −6.0% | 44% | 6.2% / 6.2% |
| new, before the frozen setup went live (19:29) | 7 | +75.8% | +48.8% | 71% | 14.3% / 14.3% |
| new, since it went live | 25 | −7.2% | −11.5% | 36% | 4.0% / 4.0% |

- **On the newest coins copying wallet 4 still pays**: +11.0% a copy against +13.6% in the backtest; 46% of all runs of 32
  copies in the backtest are as bad or worse. The bot's run: 33 copies in 25.3 hours (31 a day, the backtest 43),
  **+1.22 SOL** (+1.16 a day, the backtest +3.14): Nov 15 +2.37, Nov 16 −1.15 (Beirut days).
- **The live hours, in the model: 26 copies, −1.09 SOL; our 27 real closed trades (#38-#65): −1.0680 SOL.** The bot made
  what the backtest says these coins were worth, to two hundredths of a SOL.
- What is weaker: his pace (31 copyable buys a day against 43) and the coins that reach 3x (2 of 32 against 11.6%). Too
  few to tell from chance; the review at about trade #88 decides.
