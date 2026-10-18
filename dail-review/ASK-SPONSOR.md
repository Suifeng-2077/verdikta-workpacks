# Ask before you spend time — one message to the sponsor

You are in China. Both high-value Superteam bounties carry a region gate that is **not** in the listing description:

- `redesign-your-favourite-app-on-solana` — 1,500 USDC — **only open for people in India**
- `travel-boost-for-bp26` — 6,000 USDG — **only open for people in Germany**

A VPN does not change either. The gate is a rule on the bounty, not a network check: the API's `region` field is empty for all 12 open listings, the eligibility form has no country selector, and the restriction is rendered as page text. Whether it is enforced at submission or at judging, the thing being read is your account's country, not your IP.

But "gated" and "hard stop" are not the same thing, and I have been wrong before by assuming. The only way to know is to ask, and asking costs one message.

---

## Who to ask

The redesign listing carries the sponsor contact in its page data:

**`https://t.me/atharvelhal`** — Superteam India, point of contact for that bounty.

For BP26 the listing is Superteam Germany; their X account is `@SuperteamDE`, which is also the account you would quote-retweet.

---

## Message 1 — redesign (send this)

> Hi — I'm based in China. Before I spend time on an entry: is "Redesign Your Favourite App on Solana" open to participants outside India, or is the India region on the listing a hard eligibility requirement?
>
> I ask because the brief says "we're inviting all designers" and doesn't mention residency, so I'd rather check than assume either way. Thanks.

## Message 2 — BP26 (send this)

> Hi — I'm based in China. Is the Breakpoint 2026 travel-boost content bounty open to non-Germany participants, or is the Germany region a hard requirement?
>
> Asking before posting rather than after. Thanks.

---

## How to read the answer

| Reply | What it means | What to do |
|---|---|---|
| "Open to anyone" / "No residency requirement" | The region is the chapter's home base, not a filter | Submit. India pack: `SUBMIT.md` + `FORM-ANSWERS.md`. Germany pack: `BP26-POST-PACKAGE.md` + `deliverables/bp26/` |
| "India only" / "Germany only" | Hard gate | Drop it, do not submit, and stop counting that money |
| No reply within ~2 days | Unknown | Drop it. A gated bounty you cannot confirm is worse than a clear no, because it keeps costing attention |

---

## What I would actually do in your position

Send message 1. If it comes back "India only", then the entire Superteam surface is closed to you and the honest answer is that the only two things left on my board are the gate-free ones:

- **PR #158** — `oll4com/spaceapp`, $750, one of 16 competing PRs, maintainer has replied to none of them.
- **Go-Hybrid #448 / #451** — the only bounty programme I have found that says in writing *"Open to humans and AI: we judge the report, not the author."*

A sweep this round of every high-merge-rate repo with open bounty issues (`accensa`, `MergeFi`, `devpool-directory`, `screeps`) found **no AI policy at all** in any of them — silence, not permission. Go-Hybrid is the only one that has said yes out loud.

---

## One thing not to do

Do not set the account's country to India or Germany. It is not a bypass, it is a false statement on a submission whose winners get announced publicly and are expected to share the announcement from their own account. It would put the account at risk for 400–1,500 units of a prize that the sponsor can simply decline to pay.
