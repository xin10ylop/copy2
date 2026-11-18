# Build plan: the ladder flip (Nov 18, for the owner's OK before any code)

The research: `PREREG_ladder_flip.md` (frozen on group A; passes on groups C-F +23% to +32% a copy, and after every screen
108 coins +51% a copy, bootstrap 100%; no exit at a graduation). The forward check on every launch since Nov 18 00:00 UTC
(`../forward/f1_scan.py`) runs before anything goes live.

## What the bot must do

1. **See every pump launch's create slot.** Today the feed (`feed.rs`) subscribes to the copied wallet's transactions and
   ours. New: a filter on pump's program (every pump transaction), parsed for create events and buys.
2. **Detect the ladder** (new `ladder.rs`): for each coin created in the last few slots, the buys **in its create slot**
   whose size is within 0.005 SOL of 1.10 / 1.54 / 2.18; when 2+ different wallets, a trigger at once (SOL-priced
   curves only). Sizes, the minimum count and the tolerance in the config, so a new ladder can be added without code.
3. **Buy** on the curve directly (the long bot's own pump buy, `txb.rs`: faster than Jupiter), 0.5 SOL, in the next slot.
   No 1.25x refusal (the research paid any price); a configurable ceiling as a safety (default 5x the coin's first price).
4. **Sell** at **+20% over our own fill price** (`entry_px` in `pos.rs`; today's take profit is over the leader's price)
   or **30 s after the ladder**, whichever first; the curve completing sells as today.
5. **Run as its own unit** (`rugsnipe-ladder`), with its own wallet and config, so wallet 4's long copy is untouched.
   The existing guards apply: `max_open`, the daily stop, the KILL file, the journal (`long ladder ...` lines).

## Tests (each behaviour gets an engine test, `tests/engine_paper.rs`, and a line in `docs/20-long-copy.md` §3)

- Detection: 2 ladder sizes from 2 wallets in the create slot -> a trigger; 1 wallet -> none; the right sizes one slot
  late -> none; a size off by more than 0.005 -> none; a SOL-priced coin only.
- Exits: the take profit from our fill (not the leader's price); the 30 s cap from the ladder; the curve completing.
- Replay: the scan example (`examples/scan.rs`) over fetched transactions of real ladder launches, the bot's detection
  against `f1_scan.py`'s list.

## Rollout

1. Paper on the box for a few hours: the journal against `f1_scan.py` on the same hours (same coins, same entry slot).
2. Live at **0.1 SOL**, a mechanics test like Oct 28's: every buy and sell checked on chain.
3. 0.5 SOL if the live copies match the model. The owner decides each step.

## Risks

- One operation, seen since about Nov 15: it may stop or change its sizes (the config lets a new ladder in; the bot
  stops finding coins if it stops).
- Speed: the model enters at the first trade after the create slot + 1; a slower landing pays more.
- The feed's load: every pump transaction, parsed in the hot path (to measure in paper).

## STOPPED (Nov 18): not to be deployed

The backtest behind this plan was a model error (`PREREG_ladder_flip.md`, CORRECTION; `../churn/README.md`). The code
stays in the tree, off by default.
