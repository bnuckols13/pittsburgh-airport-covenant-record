# The PIT Terminal Financing Record

The reproducible evidence behind reporting on how Pittsburgh International's new
landside terminal was financed, and on who carries the risk if the revenue
assumptions behind it do not hold.

Open [`index.html`](index.html) first.

## The finding

Airlines are charged **$16.10** for every passenger they board at Pittsburgh,
more than at sixteen larger hubs. The Authority's consultant forecasts **$20.53
by 2030**.

The terminal's bonds carry a covenant: earnings of at least 1.25 times the annual
debt payment. The Official Statements print one combined ratio, and every forecast
year clears it. The printed figure combines two things. Separated, the airport's
**pledged Net Revenues alone come in under 1.25 in eleven of fourteen forecast
years**, and the difference is made up by a Coverage Account the Authority funds at
its own discretion, up to a ceiling of 25 percent of debt service. The forecast
assumes that ceiling is reached in twelve of those fourteen years.

**The covenant is not breached and no payment is missed in any forecast year.** The
indenture lets the Coverage Account count toward the test. The finding is what the
ratio is on pledged Net Revenues alone, in those words.

Two discretionary levers, not one. Keep them separate:

- **The Coverage Account** is funded from the airport's own Revenues, monthly, "at the
  discretion of the Authority," ninth in the flow of funds, capped at 25 percent of
  debt service. It is what closes the gap in the printed ratio.
- **Other Pledged Revenues** are something else: "moneys, not constituting Revenues,
  that are designated, for any period" into the pledge. They are counted *inside* the
  Net Revenues figure, not beside it.

The second finding is what has actually been designated. On the Authority's own
Exhibit E, the money designated from 2020 through 2023 was **federal pandemic aid in
full**, and nothing at all was designated in 2024. **No gas royalty and no gaming
revenue has been designated into the pledge in any year since 2019.** The forecast has
both resume from 2025, and from 2025 they are the entire designation.

## How to check my work

| Promise | How to check |
| --- | --- |
| The documents are the documents | `python 03-harness/fetch_sources.py` rebuilds the vault from public URLs and rejects any file whose SHA-256 does not match |
| Every claim sits on the page it cites | `python 03-harness/verify_claims.py` re-extracts each cited page and looks for the anchor text |
| The arithmetic reproduces | `02-data/coverage-table.csv` recomputes the Authority's own printed ratio from its own printed rows before decomposing it |
| The revenue itemization sums | `02-data/other-pledged-revenue-itemized.csv` reconciles to the printed total in every year but two, where the Authority's table rounds |
| Failures are published, not hidden | [`fact-check/index.html`](fact-check/index.html) lists all 77 claims. **21 currently fail.** |
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
site/                   the article
covenant/               the printed ratio decomposed
fact-check/             interactive claim ledger, filterable
01-sources-archive/     sources.json + MANIFEST.md (34 documents, hashes only)
02-data/                coverage tables, revenue itemization, cost series, benchmarks
03-harness/             fetch_sources / verify_claims / check
v2/                     the draft, the fact check, the conflicts record
```

The vault PDFs are not committed. One is 47 MB, and a reader who rebuilds them from
the public record and checks the hashes has verified more than a reader who trusts
a copy of mine.

Data is CC BY 4.0, code is MIT. Figures attributed to the Authority are its own,
archived and hashed, not independently audited here. Media clips are Tier C: an
utterance, never a figure.

Built 2026-08-31.
