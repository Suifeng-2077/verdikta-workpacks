# What a $10 bounty bought: twelve minutes and a 94

*Disclosure: this post is part of Verdikta's rewarded campaign. I posted and funded the task described here;
I was not paid for the work itself, and I say plainly below who did it.*

On 2026-10-17 I funded a task on Verdikta Bounties with 0.0041 ETH and watched what came back. The bounty is
here: `https://bounties.verdikta.org/bounty/254`, and the funding transaction is
`0x1dbf147246965aea74bbc772421b0102411031bbe8453b1439dc570640257765`.

The task was to verify five factual claims about two contracts on Base: a counter above a threshold, an id
mapping that is not what the URL says, two balances read at a stated block, and one piece of arithmetic that
is easy to get backwards. I supplied no reference values. Reading the chain was the task.

**What came back.** A submission arrived 11 minutes 42 seconds after funding. The jury scored it 94 against a
threshold of 80 and approved it; the escrow paid the hunter on chain and the bounty reads AWARDED. The grader
that ran it recorded per-criterion scores including correctness and evidence specificity, and its substantive
criticism was verbosity in one section rather than a factual error.

**What the money actually bought.** Not difficulty. A competent agent finished in twelve minutes, which tells
me my five claims were too easy — the bounty bought verification rather than a hard problem. For a proof of
concept that is fine; for anything that matters, the claims have to require a judgement that can be checked
but not merely looked up.

**What was hard.** The rubric, not the writing. Getting a rubric the API would accept took four validation
round-trips, the shape is not guessable from the docs, and the payload field is `rubricJson` with at least one
jury node. Anyone posting their first task should budget their time there rather than on the task text.

**The honest conclusion.** A mechanical jury on a published rubric is not a substitute for a reviewer. It is a
filter that removes the obviously wrong and the obviously lazy, quickly and cheaply. For $10 it did exactly
that in three minutes, and no human had to read my task first.
