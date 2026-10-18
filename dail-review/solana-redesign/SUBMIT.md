# STOP — this bounty is region-gated

**Checked 2026-10-18 against the live listing page.** The listing carries a gate string that is **not** in the bounty description and **not** in the API listing JSON:

> This listing is only open for people in **India**

`redesign-your-favourite-app-on-solana` — 1,500 USDC — is restricted to people in India. `region: "India"` in the API is not decorative; the page renders it as an eligibility gate.

**So: if you are not resident in India, this entry is not submittable and the 1,500 USDC is not available to us.** I spent many rounds treating it as the best target on the board because the description said "inviting all designers" and mentioned no residency clause. The gate lives outside the description. That was my error, and this file exists to stop it costing you time.

The same check, run across all 12 open Superteam bounties on the same day:

| Bounty | Pay | Gate |
|---|---|---|
| redesign-your-favourite-app-on-solana | 1,500 USDC | **India** |
| travel-boost-for-bp26 | 6,000 USDG (15 × 400) | **Germany** |
| rumbo-a-breakpoint-2026 | 5,000 USDG | **Spain** |
| hackyeah-superteam-poland-track | 3,000 USDC | Poland |
| colosseum-founder-support-talk-to-5-users | 1,000 USDC | gated |
| bring-your-friends-to-segmento | 500 USDC | gated |
| crea-contenido-para-promocionar-el-encuentro-2026 | 2,000 USDC | gated |
| vaultline-security-audit-grants | 40,000 USDC | open — but **audit service credit for Colosseum teams, not cash** |
| launch-and-trade-on-daejin | 620 USDC | open — 18 competing submissions |
| panta-x-nectarfi-trading-competition | 500 USDC | open — trading competition, needs capital at risk |
| create-content-on-premier-league-predictions-with-worm | 500 USDC | open — 53 submissions |
| chimp-on-metaplex | 500 USDC | open — 169 submissions |

**7 of 12 are region-gated.** Of the 5 that are open, four are crowded or not cash, and one needs money at risk.

---

## If you ARE in India, the rest of this file still applies

Everything below was prepared before the gate was found, and it is correct for the listing's own requirements. Read it as conditional.

## What the form actually asks

The listing's `eligibility` array has three text questions — this is the real submission shape, taken from the page's embedded JSON:

| # | Required | Question |
|---|---|---|
| 1 | **yes** | Which app did you redesign, and which features did you pick? |
| 2 | **yes** | What was the biggest problem you found in the current design, in 2–3 sentences? |
| 3 | no | Live link to your redesign (optional) |

So the submission is **mostly prose**, not a file upload. Answers to 1 and 2 are drafted in `FORM-ANSWERS.md` next to this file.

## The Figma step

The listing body still asks for a Figma file with before/after screens plus mobile and desktop variations. The four SVGs in `figma/` import as four frames with editable text; add a `Write-up` page inside the same file so one share link carries everything, then use Prototype → Present for the optional live link.
