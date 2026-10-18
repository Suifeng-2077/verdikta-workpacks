# Form answers — ready to paste

The listing's real submission shape (from the page's embedded `eligibility` JSON, read 2026-10-18) is three text questions, not a file upload. Two are required. Drafted answers below; both are grounded in the artefact, not in adjectives.

---

## Q1 (required) — Which app did you redesign, and which features did you pick?

**explorer.solana.com**, the official Solana Explorer. One feature: the **transaction detail page's Summary card, in its failed-transaction state** — the block that currently reduces a failure to a single red badge reading `Program Error: "Instruction #5 Failed"`.

I picked it because it is the most-read screen in the ecosystem and the one place where the data already holds the answer and the interface does not say it. The redesign is desktop and mobile of the same component, plus the before state reproduced field for field from the explorer's own source (`solana-labs/explorer`, commit `0c3256c`, `SummaryCard.tsx:61`).

---

## Q2 (required) — What was the biggest problem you found in the current design, in 2–3 sentences?

The summary tells the user which instruction failed and nothing else: not whether their tokens moved, not what it cost, and not what the error code means — the code that would explain it is computed one line earlier in the same function and then discarded. On a real failed swap I checked (`3LQ6J9Tf…cFoc67`, slot 457978450), the transaction carries seven pre- and seven post-token balance entries that are byte-identical, so "no token moved" is directly provable, yet no row on the page states it.

The page answers the question the developer asked (which step broke) instead of the question the user asked (did my money move, and what do I do now).

---

## Q3 (optional) — Live link to your redesign

Figma file, Prototype → Present share URL. Optional on the form, but the listing offers brownie points for it, so worth filling if you get that far.

---

## The one-line version, if a field is tiny

> Redesigned explorer.solana.com's failed-transaction Summary card: it says which step broke but never whether funds moved, though the transaction data answers that directly.

---

## Where the evidence lives

- `WRITEUP.md` — the full argument, the field-for-field table of the current Summary card, and every number with its source.
- `index.html` — the working prototype, one self-contained file, no build.
- `figma/` — four importable frames + `README.md`.
- `screen-desktop.png`, `screen-mobile.png` — rendered at true widths.

Every figure in these answers is reproducible with `getTransaction` on the signature above against a public mainnet RPC.
