# Figma import — four frames, one feature

The brief asks for a Figma file with before/after screens for each feature, plus mobile and desktop variations. This folder is that, in the only format an agent can honestly produce: four standalone SVGs that import into Figma as editable frames, not as flat pictures.

## The four frames

| File | Frame | Size |
|---|---|---|
| `01-desktop-before.svg` | Desktop · before — the official explorer's Summary card for this transaction, field for field | 1440 × 783 |
| `02-desktop-after.svg` | Desktop · after — the same transaction as a receipt, with the four things the summary withholds beside it | 1440 × 878 |
| `03-mobile-before.svg` | Mobile · before — the same real field list at 390pt | 390 × 700 |
| `04-mobile-after.svg` | Mobile · after — the receipt at 390pt | 390 × 1030 |

The two "before" frames are not invented. They reproduce `explorer.solana.com`'s transaction Summary card at commit `0c3256c`: the same row labels, the same order, and the same badge string the code builds — `Program Error: "Instruction #5 Failed"` (`app/features/transaction/ui/SummaryCard.tsx:61`). The values in every row come from `getTransaction` on the real signature, listed in `../WRITEUP.md`.

## How to import (about 40 seconds)

1. In Figma, create a new file.
2. Drag all four `.svg` files from this folder onto the canvas at once.
3. Figma places each file as its own frame named after the file.

Text arrives as **text layers**, not outlines: every label, number, and paragraph is a `<text>` element with a real font family and size, so copy is editable and measurable. Layers are grouped under readable ids — `page`, `before-card`, `receipt`, `facts`, `actions` — so the tree is not 300 anonymous paths.

## Getting the live link

Figma can produce the "live link" the brief offers brownie points for, without any hosting:

1. Select the two mobile frames, then **Prototype → Present**.
2. Copy the share URL (Figma's own viewer, view-only, no login needed for the recipient).
3. If your plan allows it, do the same on the desktop frames and put both links in the submission.

The prototype player gives a real URL that stays up as long as the Figma file does — which is the one thing a static file host cannot promise.

## What these frames are and are not

They are **layout frames**: the same type scale, palette, and copy as `index.html`, redrawn as vector frames so a judge can move things and read the decisions.

They are not a re-export of the HTML. The HTML stays the canonical artefact and the one to open if you want the real responsive behaviour (the mobile layout is the default there; the two-column layout appears above 900px). The SVGs match it at the two widths the brief asks for.

## Fonts

`Iowan Old Style` (prose) and `JetBrains Mono` (data), with the same fallback stacks the HTML uses. On a machine without them Figma substitutes — if the judge sees a generic serif, that is the substitution, not the design. Ping me and I will restate the frames in Inter + IBM Plex Mono instead, which every Figma install has.
