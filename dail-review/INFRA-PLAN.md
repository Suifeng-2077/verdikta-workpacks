# One small purchase that changes what I can produce

> **RETRACTED 2026-10-17 — do not buy this yet.**
>
> The central claim below was that the calibration ("does main agree with its own corpus?") cannot be
> measured without a Linux box I own. That is wrong, and I proved it wrong by reading public CI instead of
> reasoning about my own machine:
>
> - `limitlessprojects/Go-Hybrid` CI, `compiler` job, run `39040028956` on main `e2a5f7d5`, step
>   *"Checker corpus verdict agreement"*: **`verdict agreement: 55/55`**, `tripwire 2/55 = 3.6%`,
>   plus `cargo test --workspace` **128 passed / 0 failed**. Six consecutive green runs on main.
> - So main is internally consistent, on a rustc 1.99.0 Linux runner, and the result is free to read.
> - And I already hold a free Linux runner: my fork `Suifeng-2077/Go-Hybrid` reports
>   `actions/permissions → enabled=true, allowed_actions=all`, public repo. Pushing a branch there builds
>   and runs the same harness at **$0**, with no first-time-contributor approval (that gate only applies
>   to PRs into the upstream repo).
>
> Marginal value of the purchase for the purpose stated below: **approximately zero.** What it would still
> buy is iteration *speed* — a warm `target/` dir and a persistent box for heavy differential batteries —
> which is real but small, and not worth $8 when realised income to date is $1.00 against $2.30 of cost.
> Revisit only if a candidate is found and the only remaining blocker is build throughput.
>
> What actually gates the money is not tooling. See `research/ROUND-257.md`: upstream pays mostly through
> **triage verdicts and credit closes**, not through new corpus files, and that work needs no compiler.

## The short answer to "does spending a little buy a better return?"

For almost everything I have measured: **no.** Capital does not buy past a region gate, a human-review clause, or a sixteen-way race. Those are the three things that actually stopped the money, and none of them is for sale.

There is exactly one capability left that money can buy, and it is not access — it is **the ability to verify my own work**.

## What is currently blocked, and by what

The Windows host has no Rust toolchain, and cannot get one: no MSVC, and the GNU target needs a MinGW that is not installed either. Consequences, measured:

- **Go-Hybrid main pool.** BOUNTY.md says pay only after reproduction against the current checker. There is a prebuilt Windows binary, but it is `v0.1.0` (2026-10-13) while main is `a2adb61` (2026-10-17). I ran all 53 corpus files through it: **32 agree with their declared verdict, 21 disagree** — and every disagreement is in the direction "release accepts, main rejects". The binary is *looser* than main, so anything it accepts may be a false positive on main. That is why I refused to submit soundness reports: an unverified report is exactly what BOUNTY.md's anti-flood rule punishes.
- **paraloom-core.** 14 open issues, each a pre-written audit report with `file:line`, $150 each. `cargo build` is step one of its CONTRIBUTING. Cannot start.

Both of those have **no region gate** and **no human-review clause**. They are gated only by tooling. That is the one gate a small purchase removes.

## What to buy

A minimal Linux VPS. Not a GPU box, not a big one.

| | Spec | Why |
|---|---|---|
| CPU/RAM | 2 vCPU, 2 GB | the checker is a Rust workspace; it builds in minutes on this |
| Disk | 20 GB | repo is 10 MB, target dir a few GB |
| OS | Ubuntu 22.04 or 24.04 | `build-essential` + rustup, nothing exotic |
| Cost | roughly **$5–10/month** | Hetzner / Vultr / DigitalOcean all fine |
| Region | anywhere | GitHub is not region-gated; this purchase has no gate either |

Crypto-accepting hosts exist (BitLaunch, PQ Hosting), but the wallet holds 1.00 USDC and 0.0027 ETH, which is not enough, so this one goes on a card.

## What happens the moment it exists

1. `deliverables/bootstrap.sh` — one script, installs the toolchain, clones main, builds `hyb` from source, runs the corpus harness, and then runs the **calibration that matters**: every corpus file against its declared verdict, on *main* rather than on the stale release. If that prints `disagree=0`, every candidate I test afterwards is being tested against the real checker.
   Two facts the script now encodes that I got wrong the first time, both checked against the clone rather than assumed:

   - The Cargo workspace root is `compiler/`, not the repository root — there is no root `Cargo.toml`, so the obvious `git clone && cargo build` fails on the first command. The binary lands at `compiler/target/release/hyb` (package `hyb`, `[[bin]] name = "hyb"`).
   - `tools/corpus_harness.py` and `tests/checker-corpus/` are at the repository root, so the build and the corpus run need different working directories.
   - `hyb check <file> --json` exists and exits `0` for accept, non-zero for reject, and `2` for a usage error. The script reports exit `2` as an **error** rather than folding it into "disagree" — otherwise a wrong flag would read as 56 fabricated mismatches.
   - Verdict markers parse cleanly on all 56 corpus files: 40 `REJECT`, 14 `ACCEPT`, 2 `ACCEPT-MANAGED`, none unparsed.

2. Then the work that is already scoped:
   - Re-verify corpus **#53** (my open PR) on main instead of on the looser release.
   - Hunt soundness candidates **with verification**, which is the difference between a report they can reproduce and a guess.
   - paraloom's 14 issues become tractable — though its CONTRIBUTING is silent on AI, so I would start with Go-Hybrid, which says yes in writing.

## What I will not claim

- **Not a guaranteed return.** The Go-Hybrid main pool is $500 split across a top-10 per cycle, so a single accepted finding is roughly **$45–75**. The wildcard is $250 + $250 and already has 9 entries queued for the 2026-11-01 window.
- **Not a fix for the real bottleneck.** PR #158, and issues #448/#451, are all waiting on other people, not on tooling. A VPS does not make anyone merge anything.
- **Not larger than the human-gated work was.** The $1,500 redesign exists but is India-only; this purchase cannot reach it.

## What I need from you

Either:

- **Give me a shell.** Ubuntu box, an SSH key for `Suifeng-2077`'s agent, and I run `bootstrap.sh` myself and report the calibration line.
- **Or run it yourself**: `bash bootstrap.sh`, then paste me the last twenty lines. It prints the commit it built and the agree/disagree count.

The second path needs nothing from me but reading, and it tells us in one shot whether a $5–10/month box turns into verified contributions or into another dead end. If step 6 shows `disagree > 0`, main itself is inconsistent and I will say so rather than paper over it.
