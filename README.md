# The PIT Terminal Financing Record

The reproducible evidence behind reporting on how Pittsburgh International's new
landside terminal was financed, and on who carries the risk if the revenue
assumptions behind it do not hold.

Open [`index.html`](index.html) first.

## The finding

For four years nobody was paying for the new building. The Authority's audited
annual reports carry a ten-year series of what it costs an airline to board a
passenger at Pittsburgh, and the debt service line inside that calculation reads
**zero for 2021, 2022, 2023 and 2024**, because interest on the terminal bonds was
capitalized through early 2025. The audited charge fell with it, to **$7.34 in
2024**, its lowest in a decade. The first payment landed in 2025, and the
Authority's own consultant forecasts the charge climbing every year to **$20.53 by
2030**.

The bonds carry a covenant: hold at least 1.25 times the annual debt payment. The
Official Statement prints one combined ratio and every forecast year clears it.
Separated into what it is made of, the April 2025 forecast comes apart in three
layers:

| | 2025 | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---|---|---|---|---|
| Operating revenue, after expenses | 1.20 | **0.98** | **1.00** | **0.99** | 1.06 | 1.06 |
| Plus designated slot-machine money | 1.35 | 1.12 | 1.13 | 1.12 | 1.18 | 1.19 |
| Plus the Coverage Account (printed) | 1.60 | 1.37 | 1.36 | 1.37 | 1.43 | 1.44 |
| The promise | 1.25 | 1.25 | 1.25 | 1.25 | 1.25 | 1.25 |

**In 2026 and 2028 the airport's own operations do not cover its debt service at
all**, $83.0m against $84.7m and $90.2m against $90.8m. Every dollar of the promised
25 percent cushion, in all six years, is designated slot-machine tax money plus a
deposit the Authority elects to make. Footnote 1 on that table reads "Includes Other
Pledged Revenues," which is what makes the subtraction arithmetic rather than
inference.

**The covenant is not breached and no payment is missed in any forecast year.** The
indenture lets the Coverage Account count toward the test. The finding is what the
ratio is on pledged Net Revenues alone, in those words. The decomposition is ours;
the document prints only the combined column.

Two discretionary levers, not one. Keep them separate:

- **The Coverage Account** is funded from the airport's own Revenues, monthly, "at the
  discretion of the Authority," ninth in the flow of funds, capped at 25 percent of
  debt service. The forecast assumes exactly that ceiling in five of the six years.
- **Other Pledged Revenues** are something else: "moneys, not constituting Revenues,
  that are designated, for any period" into the pledge. They are counted *inside* the
  Net Revenues figure, not beside it.

The second finding is what has actually been designated. On the Authority's own
Exhibit E, the money designated from 2020 through 2023 was **federal pandemic aid in
full**, and nothing at all was designated in 2024. **Gas royalty is designated at zero
in every year from 2020 through 2030 and does not return.** Gaming money resumes in
2025, and from 2025 it is the entire designation, at $11,575,000 a year through 2030.
The airlines committed that money for 2026 through 2028. The forecast carries it to
2030 and the bonds run to 2056.

## How to check my work

| Promise | How to check |
| --- | --- |
| The documents are the documents | `python 03-harness/fetch_sources.py` rebuilds the vault from public URLs and rejects any file whose SHA-256 does not match |
| Every claim sits on the page it cites | `python 03-harness/verify_claims.py` re-extracts each cited page and looks for the anchor text |
| The arithmetic reproduces | `02-data/coverage-table.csv` recomputes the Authority's own printed ratio from its own printed rows before decomposing it |
| The revenue itemization sums | `02-data/other-pledged-revenue-itemized.csv` reconciles to the printed total in every year but two, where the Authority's table rounds |
| Figures the record does not support are held, not drawn | see `appendix-dataviz/` and `METHODOLOGY.md` |
| One command does all of it | `python 03-harness/check.py` |

## A known limit in the fetcher

Twelve sources carry a hash and are fetchable. Four of them are Post-Gazette stories
held only at the Wayback Machine, and Wayback frequently refuses or times out on a
scripted request; the Post-Gazette's own URLs return 403. `fetch_sources.py` reports
those as failed rather than passing them, and a reader who wants them will need a
browser. The remaining twenty-two sources in the manifest are Tier C media and
reference works that carry no hash and are not part of the gate.

## What is not done

The Allegheny County Airport Authority has not been asked for comment. No
Right-to-Know request and no FOIA has been sent. Nobody who bears the cost has been
interviewed. Bracketed passages in the article mark that reporting in place rather
than writing around it. This package is a working record.

## Layout

```
index.html              front door
report/                 six modules, each with the plate that carries it
documents/              every source, graded and searchable, with what each proves
factcheck/              the two machine gates, the conflicts register, the held claims
appendix-dataviz/       the plates
covenant/               the printed ratio decomposed
model/                  the slider model on the Authority's own forecast rows
01-sources-archive/     sources.json + MANIFEST.md (34 documents, hashes only)
02-data/                coverage tables, revenue itemization, cost series, benchmarks
03-harness/             fetch_sources / verify_claims / build_tools / check
v2/                     the conflicts record
```

The vault PDFs are not committed. One is 47 MB, and a reader who rebuilds them from
the public record and checks the hashes has verified more than a reader who trusts
a copy of mine.

Data is CC BY 4.0, code is MIT. Figures attributed to the Authority are its own,
archived and hashed, not independently audited here. Media clips are Tier C: an
utterance, never a figure.

Built 2026-09-01.
