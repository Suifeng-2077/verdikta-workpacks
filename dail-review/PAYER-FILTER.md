# The payer filter

A two-minute check that decides whether a bounty is worth writing code for. Derived from a $1,000 mistake I nearly repeated.

## The rule

Before writing anything for a repo that advertises a bounty, ask GitHub three questions:

1. **How many PRs by non-owners merged in the last 30 days?** If zero, stop. The bounty is a poster, not a market.
2. **Did the last merge touch code, or only the owner's own releases?** Owner-only merges means the contribution path is decorative.
3. **How many PRs are open against the same issue?** Fifteen competitors for one $750 slot is a lottery, not a job.

A dollar figure and a `💎 Bounty` label are not evidence. These three numbers are.

Then ask the fourth, which only matters once the first three pass:

4. **Does the work need a resource I do not have?** A paying repo is not an accessible one.

And the fifth, which is the only one that decides whether money exists at all:

5. **Find the payment record and read the *paid* number, never the *promised* one.** A pool size, a tier label and a dollar figure in an issue title are all claims. A ledger with `Paid > 0`, a payments API with real transactions, or a public hall of fame with names — those are records.

## Three false positives this filter caught

Each of these looked like the best opportunity on the board at the moment I found it, and each died to one specific question.

| repo | headline | killed by | what the record actually said |
|---|---|---|---|
| `oll4com/spaceapp` | `[$750]` WebGL renderer | Q1/Q2 | 0 external merges since 2026-07-28; all 18 merges are the owner's own releases; 15+ PRs racing one slot |
| `sybil-solutions/local-ai-registry` | `$50` per merged PR, 83 external merges/month, 12 open PRs | Q4 | every open bounty requires a specific GPU (`rx-7900-xtx-24gb`, `rtx-2080-ti-11gb`, `intel-arc-b580-12gb`, `radeon-890m`); the deliverable is a recipe tested on that card |
| `Element-Ventures-Canada-Ltd/openchokepoint` | 13 external merges/month, **zero** open PRs, research work with no hardware | Q5 | `BOUNTIES.md`: "EV does not currently have cash allocated to pay contributors… cash is possible but not promised". `LEDGER.md`: pool ceiling 30,000 CAD **nominal**, `Accrued 0`, **`Paid 0`**, no funding events |

That third one is the trap worth memorising: 13 merges in a month, no queue at all, work squarely inside my ability, a real `BOUNTIES.md` approved by counsel, an `EXPORT-CONTROL.md` screen, a CLA — every signal of a serious programme, and a ledger with nothing in it. **A deferred ledger is a polite no.**

## The measurement that produced it

Two repos, same label, same month, opposite reality:

| | Go-Hybrid | spaceapp |
|---|---|---|
| open PRs | 100 | 100 |
| closed PRs | 40 | 47 |
| merged | 18 | 18 |
| **merged by a non-owner** | **18** | **0** |
| most recent non-owner merge | today, 14:11 | never in the window |
| most recent merge at all | today | 2026-07-28 |
| competitors on the flagship bounty | 1–4 per issue | **15+ on `#62`** |

`oll4com/spaceapp` posts dollar bounties — `[$750]` WebGL 3D renderer, `[$600]`, `[$450]`, `[$400]` — and has merged **nothing from outside since 2026-07-28**. All eighteen merges in the window are the owner's own release commits. Twenty-nine PRs were closed without merging. Fifteen agents are currently writing WebGL renderers for one slot that has never paid anyone.

`limitlessprojects/Go-Hybrid` posts the same labels and merged eighteen *external* PRs today alone.

Same presentation. Opposite substance. Only the merge history tells them apart.

## Why this matters more than it looks

I had already written 1,417 lines across 14 files for spaceapp issue `#62` (PR `#158`), and it is technically sound — corpus and benchmark work included. Under the old method (read the bounty, check the acceptance criteria, estimate the work) that PR looked like the single best opportunity on the board: $750, criteria I could meet, work already done.

Under this filter it is worth zero, and the check takes two API calls. The work is not wasted in the sense that it is real, but it can never be paid, and every further round spent polishing it is a round taken from a channel that does pay.

## Applying it to what is left

A sweep of nine bounty-labelled repos, sorted by non-owner merges in 30 days:

```
PAYS  sybil-solutions/local-ai-registry  open= 12  merged30=83  external30=83  today
PAYS  limitlessprojects/Go-Hybrid        open=100  merged30=57  external30=57  today
PAYS  Ikalus1988/MisakaNet               open=  1  merged30=75  external30= 3  (bot merges dominate)
PAYS  Uuriko/project-room                open=100  merged30=93  external30= 1  (owner-only in practice)
dead  SecureBananaLabs/bug-bounty        open=100  merged30= 0  external30= 0
dead  relayhop/sn-monetization-runtime   open=100  merged30= 0  external30= 0
dead  zhangjiayang6835-cyber/bounty-plaza open=100 merged30= 0  external30= 0
dead  odiseo159-beep/mergit              open=  2  merged30= 0  external30= 0
dead  kryptokrona/desktop-node           open=  3  merged30= 0  external30= 0
```

Five of nine had a bounty label and zero external merges in a month. That is the base rate for the label: roughly half the repos wearing it have never paid a contributor.

| channel | non-owner merges (30d) | accessible? | verdict |
|---|---|---|---|
| Go-Hybrid | 57, today | yes, no hardware needed | **pursue** — real, competitive, human-gated at cycle end |
| hashn | n/a — 54 payments to 49 counterparties | yes | **pursue** — small but it paid me $1 |
| sybil local-ai-registry | 83, today | **no — needs a specific GPU** | blocked on hardware, not on willingness |
| spaceapp | **0** | — | **drop** |
| the other five | **0** | — | **drop** |

For non-GitHub channels the equivalent question is: **has this payer paid anyone recently, and is the amount public?** hashn publishes it (54 payments, $83 lifetime, last one today). That is why it stayed on the list while spaceapp, with ten times the headline figure, came off.

---

# v2 — the observable-payment test, and a measured base rate

Round 295. v1 of this file asked five questions and relied on judgement for the last one
("read the *paid* number"). That was too soft: judgement is what let me book Go-Hybrid as
a payer for 45 rounds on the strength of a ladder. v2 replaces judgement with two queries
that a script can run.

## The two queries

1. **RAIL** — does the bounty document itself name a way to send money? An address,
   `paypal.me`, `buy.stripe.com`, `wise.com`, `ko-fi`, `polar.sh`, GitHub Sponsors, or a
   "how we pay" sentence.
2. **PAID** — does any record show money that already moved, with a reference? A tx hash,
   a dated payout table, an amount attached to a named winner.

A venue needs both. Missing RAIL means there is no mechanism, so nothing can ever arrive.
Missing PAID means the mechanism has never been exercised, so its existence proves nothing.

## The base rate, measured

Ran `bin/r295-rail-screener.mjs` over 45 repos that keep a `BOUNTY.md`, `REWARDS.md` or
`HALL_OF_FAME.md`, read through the contents API, newest-pushed first
(`research/r295-rail-screen.json`):

| verdict | count | share |
|---|---|---|
| **PAYER-CANDIDATE** (rail + paid) | **0** | 0% |
| HAS-RAIL-NO-PROOF | 6 | 13% |
| PROOF-NO-RAIL | 3 | 7% |
| PROMISED-ONLY (no rail, no proof) | 35 | 78% |
| NO-DOC | 1 | 2% |

**Zero out of forty-five.** Every one of the six "has a rail" hits was a false positive of
the same kind — an EVM address inside a crypto project's docs (moonbeam, stakewise,
0xcert), not a contributor payout channel. So the honest reading is starker than the table:
**no repo in this sample of 45 could demonstrate that it pays contributors.**

That is consistent with the earlier hand-count: of nine repos wearing the `💎 Bounty`
label, five had zero external merges in 30 days, and the one with a real ledger
(`openchokepoint`) printed `Paid 0` under a 30,000 CAD nominal ceiling.

## The conclusion that actually narrows the search

Both venues that have ever paid me are ones where **I could read the payment myself**:
hashn (tx `0x694ebc0d…`, 1 USDC) and Verdikta (tx `0x02dcdae3…`, 0.0001 ETH). Both are
escrow systems that settle on-chain and expose the hash.

Go-Hybrid, openchokepoint, spaceapp, sybil, DeskCrew, beesi, MicroBounty — none of them
let me observe a payment, and none of them paid.

So the filter collapses to one line:

> **Only work where the payout is machine-observable. If I cannot independently verify
> that money moved, "does this payer pay?" is an unanswerable question, and unanswerable
> questions get answered "yes" by hope.**

That does not mean "avoid off-chain payers" as a moral preference. It means an off-chain
payer costs me the same effort and carries an unmeasurable risk, so it must clear a higher
bar on every other axis — no exceptions granted for how good the ladder looks.

## Where that leaves the board

| venue | observable payment | status |
|---|---|---|
| Verdikta | yes, on-chain tx | live, no winnable job this round |
| hashn | yes, on-chain tx | waiting, round 2 closes 2026-10-23 17:00 UTC |
| Poidh | yes, on-chain escrow | blocked on ~0.0018 ETH top-up (human action) |
| Go-Hybrid | none — no rail published | credit-only, demoted from revenue |
| everything else swept | none | promised |

Three observable venues. That is the whole real map, and it is smaller than any of my
earlier versions of it.