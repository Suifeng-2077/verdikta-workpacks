# What is actually left, after round 244 — rewritten because two thirds of it was gated

**Correction first.** For something like forty rounds I have been quoting "$1,900 waiting on you" — the 1,500 USDC Solana redesign plus the 6,000 USDG BP26 travel boost. Both are **region-gated**, and the gate is not in the listing description:

| Bounty | Pay | Gate (read off the live page 2026-10-18) |
|---|---|---|
| redesign-your-favourite-app-on-solana | 1,500 USDC | **only open for people in India** |
| travel-boost-for-bp26 | 6,000 USDG | **only open for people in Germany** |
| rumbo-a-breakpoint-2026 | 5,000 USDG | **only open for people in Spain** |

7 of the 12 open Superteam bounties carry such a gate. The five that do not are: an audit-credit grant that pays no cash, a trading competition that needs capital at risk, and three content bounties with 18, 53 and 169 competing entries. **There is no globally-open, high-value, low-competition Superteam bounty right now.**

So the honest position is: unless you are resident in India, Germany or Spain, none of that money is ours. Everything I said about "the best odds on the board" was built on a field I never read. The deliverables still exist and are good; they are just aimed at a door with a lock on it.

Everything below is what survives.

---

## 1. spaceapp #62 — $750 — submitted, 1 of 16 — **no region gate**

**PR #158: https://github.com/oll4com/spaceapp/pull/158**

13 files, +1297/−78, `mergeable: true`, snyk passed. Measured: p95 frame 6.4 ms against a 33 ms target at 50,000 nodes, 0 long tasks over 100 ms, GPU picking p95 0.4 ms.

What moves the odds: the maintainer has engaged with **none** of the 16 PRs, so nobody is ahead. His stated terms require that a person reviewed and tested the work — that person is you, and ten minutes on this PR is worth more than a new build.

---

## 2. Go-Hybrid — issue #448 and PR #451 — **no region gate**

`limitlessprojects/Go-Hybrid`, whose BOUNTY.md says in as many words: *"Open to humans and AI: we judge the report, not the author."* The only venue I have found that does not require a human to vouch for my work.

- **#448** — wildcard proposal on deadlock-freedom: close-right linearity + structured spawn, with the sacrifice and the falsifiers named. Pays $250 on acceptance + $250 on published learning, failure included. Awaiting triage (they commit to 48h).
- **#451** — corpus fixture #53. Verdict `REJECT A1c` was **verified** with their official v0.1.0 Windows binary (`HYB-E3002`), after calibrating that binary against all 53 corpus files (32 agree, 21 disagree — the release is looser than main). CI is `action_required`, waiting for a maintainer to approve a first-time contributor's workflow.

---

## 3. The rest of the board, honestly

- **Cantina v4lend, $50,000** — 1,750 findings filed, joining restricted. Not reachable for a first-time entrant.
- **paraloom-core, 14 × $150** — real merge history, but 88 open PRs and no stated AI policy; silence is not permission. Rust toolchain also unavailable here.
- **The agent-economy boards** — hashn is one payer and paid me 1 USDC; DeskCrew's board is `count: 0`; Agent Souk: 3,626 agents, zero peer-to-peer settlements.

---

## What I would do with your next thirty seconds

If you are in India, Germany or Spain, say which, and the corresponding pack is ready to submit within minutes (`deliverables/solana-redesign/SUBMIT.md` + `FORM-ANSWERS.md` for India; `deliverables/BP26-POST-PACKAGE.md` for Germany).

If you are not, then the only two things that can still pay are PR #158 and the Go-Hybrid pair, and both are waiting on other people, not on more work from me.
