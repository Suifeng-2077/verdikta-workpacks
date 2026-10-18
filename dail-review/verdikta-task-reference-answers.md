# Reference answers for the funded task (self-check before spending)

I ran my own five claims before funding, because a task nobody can answer burns the 24-hour
window for nothing. All five are answerable from public data in about ten minutes.

Read at Base block 52733443.

| # | claim | reference answer | verdict |
|---|---|---|---|
| 1 | Poidh `bountyCounter()` > 500 | **508** | CONFIRMED |
| 2 | #1489's on-chain id differs from its URL id | URL **1489** → on-chain **503**. Mapping from `poidh.xyz/bounties/data`, which carries both fields; sanity check: URL 1493 → 507 and the counter reads 508, so on-chain ids run 0..507 | CONFIRMED |
| 3 | Verdikta escrow `0xA741…` holds > 0.01 ETH | **0.0695 ETH** | CONFIRMED |
| 4 | `0xb380…f622` holds exactly 1.000000 USDC | **1.000000** | CONFIRMED |
| 5 | USDC/WETH 0.01% pool `slot0` tick and implied price | tick **-198495**; with token0=WETH(18dp) and token1=USDC(6dp), USDC per ETH = 1.0001^tick × 1e12 = 2.3983e-9 × 1e12 = **2398.30** | answerable |

Two things this self-check bought:

- **The arithmetic trap is real.** My own first pass used `1.0001^-tick` and produced 4.2e20 USDC per
  ETH. The task asks the hunter to show the arithmetic precisely because that sign is easy to flip,
  and now I can grade it without having to trust the submission.
- **Claim 2 is the one that costs time, not skill.** Nothing on the bounty page says the URL id is
  not the on-chain id, and a direct contract read with the URL id reverts. That is the difference
  between a five-minute answer and an hour, which is what makes it a fair $10.

State at the time of writing: #1489 still shows `hasClaims: false` — zero claims, so a first valid
claim is still available.