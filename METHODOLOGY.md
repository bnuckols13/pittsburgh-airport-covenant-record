# Methodology

## What this package claims, and what it does not

It claims that a set of figures printed in the Allegheny County Airport Authority's
own bond documents, when separated into their components, show something the
combined printed figure does not show. It does not claim the Authority has breached
its covenant, missed a payment, or done anything the indenture forbids. On the
covenant as written, which lets the Coverage Account count toward the 1.25 test,
every forecast year complies.

## Tiers

- **Tier A.** A primary document, captured and hashed: an Official Statement, an
  FAA circular, a published rate schedule, a public notice.
- **Tier B.** An official but secondary record.
- **Tier C.** Media. A clip may establish that somebody said something. It may
  never be the source of a figure.

## The two gates

**The hash gate** re-hashes every cited document against the SHA-256 in the ledger.
A document that has been re-captured, re-paginated or silently revised fails here.

**The anchor gate** re-extracts each cited page and looks for the literal run of
text a claim rests on. A figure that has moved off the page it was cited from stops
being citable, and the run exits non-zero rather than hand over a draft resting on it.

Pages are extracted two ways, with `pdftotext -layout` and `pdftotext -raw`, and an
anchor is satisfied if it appears under either. Both are deterministic. The reason
for two is that the financial tables in these Official Statements survive one mode
or the other and not reliably both: `-layout` preserves the visual grid but splits a
transposed table's row label away from its figures, while `-raw` keeps a printed row
contiguous and loses column alignment. Checking one mode only produced fourteen false
misses on rows whose figures were plainly present.

## Citing pages

Pages are cited as `PDF n (printed n)` because in the 2025 Official Statement the two
differ by ten. PDF 57 is the statements of revenues; printed 57 is a different section
entirely.

## Vintages are kept separate

The 2021, 2023 and 2025 Official Statements each contain a forecast. They are three
forecasts, not one series, and no figure is carried across them or summed. Where two
of them disagree, both are recorded.

## Where a document contradicts itself

It is disclosed and neither figure is chosen. The 2025 statement gives two different
2023 figures for cost per enplaned passenger and two for Other Pledged Revenues.
Both pairs are recorded in `v2/CONFLICTS-2026-08-31.md` and in the data files, with
the page each came from.

## Two bases of cost per enplaned passenger

The Authority's residual calculation and FAA CATS Form 5100-127 are different series.
For 2024 they read $11.56 and $12.19. The basis is named wherever the figure appears,
and the two are never subtracted across each other.

## What the reporter computed

The decomposition of the coverage ratio is ours. The Official Statements print only
the combined figure. Before decomposing, `coverage-table.csv` reproduces the
Authority's own printed ratio from its own printed rows, so that the decomposition
can be checked as arithmetic rather than accepted as interpretation. Every computed
percentage is labelled as computed in the passage where it appears.

## Known gaps

The Authority has not been asked for comment. No records request has been sent. No
person who bears the cost has been interviewed. The master plan alternatives analysis,
which is the document that would settle whether renovating was in fact more expensive,
has never been published and is the subject of an unsent Right-to-Know request and an
unsent FOIA.
