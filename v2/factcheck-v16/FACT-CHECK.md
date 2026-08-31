# Fact check: the Aug. 30 draft

Checked 2026-08-30. 77 claims out of the draft. 21 fail, 6 have no located source, 30 need a qualification settled, 19 check out, 1 is a bracketed slot.

Article checked: sha256 `7ed912d3398ebfa7acbebd31d6873af420d52f98be569336091b9473878d9435`

Against the previous draft: 38 claims are new, 19 carried over and hold, and 20 carried over with the defect the last pass named still in place.

Machine-readable ledger: [`factcheck.json`](factcheck.json). Annotated draft: [`ARTICLE-v16-ANNOTATED.md`](ARTICLE-v16-ANNOTATED.md). What to go get: [`QUERIES.md`](QUERIES.md).

## What changed since the last pass

**Fixed.** KBRA is now correctly A+ rather than A. Pittsburgh's medium-hub status is now on the page, which was the largest missing qualification in the peer comparison. The Allegheny Institute's $75 million is no longer set against a single hard debt figure. The gas royalty range is given to the cent. The covenant section now carries three cautions in its own voice, including the capitalised-interest footnote and the three-way mismatch between the Coverage Amount, the designated series and the airlines' commitment, and those cautions are correct.

**New and strong.** The 11-of-14 and 12-of-14 counts, the two-vintage dumbbell, the gap ranges, the reproduction check on the printed ratios, and the Event of Default cure provision all reproduce exactly from the printed rows. That section is the best-built writing in either draft.

**Carried forward unfixed.** The Cassotis renovation quotation is still sourced to an uncaptured broadcast. The designated-revenue money is still described as gas and casino money when the Authority's own exhibit itemises it as federal pandemic relief. Koopmans is still Thijs. The KBRA sentence is still a paraphrase inside quotation marks. The demolition maintenance figure is still called undisclosed when it is disclosed at $2,047,000 a year. The 2025 enplanement claim is still unsupported.

**New failures.** The headline's 'never been higher' is wrong on the Authority's own table. The (AP) dateline is not the outlet's. The October scene is not the opening. Four members of the congressional delegation were there. The grant share, the debt-service total, the capacity band, the 9.95 million, Spirit's exit, the covenant survey, Fraport, Grant Oliver and the website claim are all wrong on the record.

## Method

Every sentence of the Aug. 30 draft was split out and given a claim ID. Each claim was re-checked against the primary record rather than against the case's earlier findings. The eight vault PDFs were re-hashed against their .sha256 sidecars, all eight matched, and their text was extracted page by page so every figure could be located at PDF n (printed n). Quotes attributed to news accounts were checked against the captured, hashed HTML in the pit-tier1-media-archive sibling. Sources outside the vault were fetched and read during this pass. Claims that also appeared in the previous draft carry a marker saying whether they were fixed or carried forward unchanged.

All eight vault documents verified against their recorded hashes, and all 66 claim anchors located on the pages they cite.

## Standings used

| Standing | What it means |
|---|---|
| **FAILS** | The cited record does not support the sentence as written. |
| **UNSOURCED** | No located source in the case, the vault or this pass. |
| **ATTENTION** | Accurate as far as it goes, and carrying a qualification, a basis, a vintage or an omission that has to be settled before print. |
| **VERIFIED** | Supported, to the figure or to the word, by a hashed primary in the vault or by a source read in full during this pass. |
| **SLOT** | Bracketed in the draft. Blocked on reporting that has not happened. |

## The 21 that fail

Each says something the cited record does not say. Ordered as they appear in the draft.

### D-001 · Headline · New in this draft

> Pittsburgh built a $1.7 billion airport terminal. What it costs airlines to fly there has never been higher.

**Where it was checked.** pdf 170 (printed 53), Table IV; pdf 62 (printed 52)

**What the record says.** Table IV, Rates and Cost Per Enplaned Passenger, last ten fiscal years to 2023: 2023 $11.50, 2022 $10.58, 2021 $12.33, 2020 $20.50, 2019 $9.77, 2018 $10.30, 2017 $12.76, 2016 $12.86, 2015 $12.89, 2014 $13.91. The MD&A table at pdf 62 gives 2020 as $20.57.

**Standing.** FAILS. The charge was higher in 2020, at $20.50 on the audited basis and $20.57 as the Authority reports it in the same statement. $16.10 is the highest since 2020 and the highest in a normal year, which is a true and printable sentence. 'Has never been higher' is not, and it is the headline. 'Built' also carries the budget-versus-spend problem from the last pass: $1.7bn is the approved ceiling and the February 2025 spend was $1,395,561,842.

### D-003 · Dek · Carried from v15 with the same defect

> The gap is closed with casino and gas money the Authority decides on once a year and is under no obligation to provide.

**Where it was checked.** pdf 316 (Exhibit E); pdf 32; pdf 67 (printed 57)

**What the record says.** Exhibit E itemises Other Pledged Revenues by component, 2019 through 2030. Discretionary (Gas) Revenues: $3,815k in 2019 and zero in every year 2020 through 2030. Discretionary (Gaming) Revenues: $1,730k in 2019, zero 2020 through 2024, $8,170k in 2025, then about $8,100k to $8,500k a year with Supplemental Gaming for BHS on top. The flow of funds at pdf 32 provides for deposits to the Coverage Account 'on or prior to the tenth (10th) Business Day of each month, at the discretion of the Authority.' In connection with the January 2025 MII vote the Authority committed to no less than $8.8m for 2025 and $11.575m a year for 2026 through 2028.

**Standing.** FAILS on all three clauses, and this is the same failure the last pass found in the last draft's dek. Gas is designated at zero in every forecast year, so the money closing the gap going forward is gaming, not 'casino and gas.' The deposit is monthly at discretion, not annual. And the Authority is under an obligation, through 2028, of no less than $11.575m a year, which the story itself reports two sections later. The draft's own plate note gets this right where the dek does not: no document states that the designated revenue is the source that closes this particular gap.

### D-004 · Scene · New in this draft

> PITTSBURGH (AP) —

**Where it was checked.** No record cited.

**What the record says.** The byline three lines above reads 'By [Reporter] | Public Source | Aug. 30, 2026'.

**Standing.** FAILS, and it is the most immediately damaging error in the draft. An (AP) dateline attributes the story to the Associated Press. It is not an AP story. This appears to be an artifact of the v6 apparatus note, which used 'PITTSBURGH (AP)' as an illustration of a dateline the outlet would set and said in terms that it is 'theirs to set, not the draft's.' Cut it, or set 'PITTSBURGH' alone.

### D-005 · Scene · New in this draft

> On a morning in October ... a building that opened eight years after the board approved it

**Where it was checked.** No record cited.

**What the record says.** The Authority's own release is headed 'Transformed Pittsburgh International Airport Opens Today' and is dated Nov. 18, 2025. The October event was Saturday, Oct. 11, 2025: a ribbon-cutting for about 300 invited guests at 9:30 a.m. followed by a registration-gated community open house from noon to 7 p.m.

**Standing.** FAILS. The October morning was not the opening. The terminal opened on Nov. 18, 2025, five and a half weeks later, with a United arrival from San Francisco and a Southwest departure to Denver. The whole scene is written as opening day and the graf says so. Either move the scene to November or write the October event as what it was, which is a ribbon-cutting and an open house. Sept. 12, 2017 to Nov. 18, 2025 is eight years and two months, so 'eight years' survives either way.

### D-006 · Scene · New in this draft

> no one from the congressional delegation that had been announcing federal checks for the project since 2021 had come out to the airfield that day to say anything unkind

**Where it was checked.** No record cited.

**What the record says.** The West Hills Gazette account of the Oct. 11 ceremony names Rep. Chris Deluzio, Rep. Summer Lee, Rep. Mike Kelly and Sen. Dave McCormick among those who attended or spoke.

**Standing.** FAILS as written. Four members of the delegation were there. The sentence's plain reading is that none came. If the intended point is that none of them criticised the project, say that, and name them: it is a stronger sentence with four names in it than with an absence. Note also that the [TK others] two grafs down is answered by the same source.

### D-015 · Nut · Carried from v15 with the same defect

> what the airport charges the airlines works out to $16.10 for every passenger they board, the highest figure in the airport's history

**Where it was checked.** os-2025ab pdf 170; pdf 62

**What the record says.** 2020 was $20.50 on Table IV and $20.57 in the MD&A. $16.10 is FAA CATS Form 5100-127 line 1.7 for fiscal 2025, and appears in none of the eight hashed documents. The Post-Gazette of Jan. 11, 2026 reports the airport's own 2025 figure as a projected $16.69 and its 2026 expectation as $17.64.

**Standing.** FAILS three ways. It is not the highest in the airport's history. It is a fiscal 2025 figure in a story dated August 2026, when the Authority's own current-year expectation is $17.64. And it is on the federal-filing basis while the sentence beside it, and the $11.34 two grafs later, are on the Authority's residual basis. The case's own rule is to name the basis or not print the comparison. Pulling the FY2025 and FY2026 Form 5100-127 fixes all three at once and is the single cheapest capture in the queue.

### D-019 · Nut · New in this draft

> Every estimate the Authority gave the public before it sold the bonds came in under what followed, and the gap has widened in every year since.

**Where it was checked.** os-2021ab pdf 185; os-2025ab pdf 62

**What the record says.** 2021 OS base case against the Authority's later actuals: 2021 forecast $12.76 against actual $12.35, so the forecast was 3.3 percent ABOVE the outcome; 2022 $9.78 against $10.57; 2023 $9.73 against $11.34; 2024 $9.83 against $11.56.

**Standing.** FAILS on both halves. The 2021 forecast overshot the 2021 actual, so not every estimate came in under what followed. And the gap does not widen in every year: it is negative in 2021 before turning positive and growing 2022 through 2024. The true version is that from 2022 onward every year came in above forecast and the miss grew each year, which is three years of a widening gap and still a finding.

### D-022 · Covenant · Carried from v15 with the same defect

> that account holds royalties from gas wells drilled on airport land and Pennsylvania's tax on slot machines ... It designated $19.1 million of that money into the pledge in 2021 and $3 million in 2023.

**Where it was checked.** pdf 316 (Exhibit E); pdf 61 (printed 51); pdf 295

**What the record says.** Exhibit E itemises the 2021 total of $19,146k as CARES/CRRSA/ARPA (PIT) $18,183k, CARES (BHS Credit) $905k and CARES/CRRSA/ARPA (AGC) $57k. It is federal COVID-19 grant money in full. The 2023 figure at Exhibit E is $4,040k of CRRSA/ARPA concession grants, against $3,029k for the same line at pdf 61. Discretionary gas and gaming are both zero in 2021 and 2023. Table 17 at pdf 295 shows the same, with 'Discretionary (Gas) Revenues 0.0%' and 'Discretionary (Gaming) Revenues 0.0%' for 2023 and 2024.

**Standing.** FAILS, and it is the same failure the last pass found. The $19.1 million and the $3 million were not gas and casino money. They were federal pandemic relief. The statement also gives two figures for 2023, $3,029k and $4,040k. And the Coverage Account is not where Other Pledged Revenues sit: they enter Net Revenues, while the Coverage Account is fed from Revenues generally. The story that this exhibit actually supports is that gas and gaming stopped being designated after 2019, federal relief stood in until 2023, nothing was designated in 2024, and gaming resumes in 2025 under the airlines' own vote.

### D-030 · Covenant · New in this draft

> One survey of 57 United States airport bond documents put the share permitting this sort of transfer at 59 percent, naming Austin, Los Angeles and San Francisco. That survey is a consultant's compilation, undated

**Where it was checked.** No record cited.

**What the record says.** The page reports '30 of the 51 (59%)' carrying soft coverage covenants, with 57 documents as the wider corpus behind the article's structural provisions. The airports it names in that discussion are the City of Austin and Dallas Love Field. It carries a banner reading 'DWU AI Product' and the disclosure that 'DWU AI articles are produced with rigorous AI review but may contain mistakes.' It is dated April 20, 2026 and last updated May 2, 2026.

**Standing.** FAILS on three counts. The 59 percent is 30 of 51, not a share of 57. Los Angeles and San Francisco are not the airports the page names for this finding; Austin and Dallas Love Field are. And the source is not an undated consultant's compilation: it is a dated, self-declared AI-generated article that warns on its face that it may contain mistakes. The draft's instinct to hedge is right and its description of what it is hedging is wrong. Given that the sentence exists only to say the arrangement is not unusual, the cleanest fix is to pull three or four peer Official Statements and say it from primaries, or cut the sentence and let the Pittsburgh forecast stand alone.

### D-037 · What it costs · Carried from v15 with the same defect

> KBRA, which rated the 2025 bonds A+, listed among the credit challenges that "a rising CPE could discourage service expansion or retention, particularly for LCCs and ULCCs."

**Where it was checked.** No record cited.

**What the record says.** The KBRA presale is not in the vault and the phrase appears in none of the eight hashed documents. The case's own apparatus records it as a paraphrase carried into a findings file.

**Standing.** FAILS, unchanged from the last pass. The A+ is now right, which is a fix. The quotation marks are still around a paraphrase, and that is the exact defect the quote gate was built to catch and did catch in eight earlier rows. Obtain the presale or drop the quotation marks.

### D-038 · What it costs · New in this draft

> Spirit Airlines left Pittsburgh on May 1, 2026, and traffic fell 1.1 percent.

**Where it was checked.** No record cited.

**What the record says.** Spirit ceased all operations nationwide; the final flight landed early on May 2, 2026, after nearly 34 years. The Authority's own outlet reports Spirit as PIT's sixth largest carrier at 3.5 percent of total traffic as of March 2026, having peaked near 10 percent. WPXI of Aug. 14, 2026 reports PIT traffic down 1.1 percent year over year for the first six months of 2026, 4.67 million against 4.7 million, and attributes it to 'Spirit Airlines' demise and higher fuel prices industrywide.'

**Standing.** FAILS, and the placement makes it worse. Spirit did not leave Pittsburgh; Spirit stopped existing. Put in a paragraph about a rising charge discouraging low-cost carriers, the sentence implies Pittsburgh's cost drove the exit, which nothing supports. The date is May 2, not May 1. The 1.1 percent is a first-half 2026 year-over-year figure with fuel prices named alongside Spirit, and the draft gives it no period at all. This is the kind of sentence that, if it runs, hands the Authority the whole paragraph.

### D-041 · What it costs · Carried from v15 with the same defect

> Thijs Koopmans and Rogier Lieshout, writing in the Journal of Air Transport Management in 2016

**Where it was checked.** Journal of Air Transport Management 53 (2016) 1-11, doi:10.1016/j.jairtraman.2015.12.013

**What the record says.** Authors of record: C.C. Koopmans and R. Lieshout. The first author is Carl Koopmans, professor at Vrije Universiteit Amsterdam and SEO Amsterdam Economics. No aviation economist named Thijs Koopmans exists, and none has co-published with Lieshout.

**Standing.** FAILS, unchanged from the last pass. Carl, not Thijs. The characterisation of the finding is exact, to the word, in both directions. One given name is all that stands between this and the best citation in the piece.

### D-049 · 2028 · New in this draft

> The Authority borrowed about $1.66 billion across three bond sales ... and owes about $2.5 billion in principal and interest by the time the last of it matures in 2056.

**Where it was checked.** pdf 39; pdf 147; pdf 1 of each vintage

**What the record says.** Par: 2021A $719,850,000 and 2021B $112,820,000; 2023A $346,960,000, 2023B $27,065,000 and 2023C $41,000,000; 2025A $361,675,000 and 2025B $48,840,000. Total $1,658,210,000. The combined debt service schedule at pdf 39 totals $3,232,650,565.06, made up of $2,387,078,474.23 on the prior bonds plus $761,217,582.26 on 2025A and $84,354,508.57 on 2025B. The $2,504,998,449 figure is the financial-statement note at pdf 147 and covers only the $1,247,695,000 outstanding before the 2025 issuance.

**Standing.** FAILS. The $1.66 billion correctly includes the 2025 sale and the $2.5 billion does not, so the sentence pairs a three-sale principal with a two-sale debt-service total. Total principal and interest to 2056 is about $3.23 billion. Fixing it makes the sentence worse for the Authority, which is a reason to fix it.

### D-053 · The test · Carried from v15 with the same defect

> In 2025 passengers again beat the base case and the charge landed at $16.10, three cents above the slow-growth case

**Where it was checked.** os-2021ab pdf 185

**What the record says.** 2021 base case 2025 enplanements 5,086 thousand; 2025 statement base case 5,064 thousand. The case's only 2025 figure is an estimate of 4,904.2 thousand, below both. The slow case 2025 CPE is $16.07 and the FY2025 CATS figure is $16.10. The Authority's own 2025 figure, in the Post-Gazette of Jan. 11, 2026, is a projected $16.69.

**Standing.** FAILS on the first half, unchanged from the last pass. The 2025 enplanement actual has never been fixed and the only figure the case holds points the other way. The three-cent line pairs a federal filing against an Official Statement forecast, and on the Authority's own $16.69 the margin is 62 cents rather than three. A finding that moves twentyfold with the basis cannot run without naming the basis.

### D-058 · The test · New in this draft

> the Authority publishes no cost-per-enplanement figure on its own website

**Where it was checked.** No record cited.

**What the record says.** flypittsburgh.com posts annual financial reports for 2015 through 2025 on its Reports and Financials page, and each carries Table IV, Rates and Cost Per Enplaned Passenger, in the statistical section. The version of that table reproduced at os-2025ab pdf 170 prints ten years of the figure. The Authority's own Blue Sky News has also published the figure, and the Authority gave the Post-Gazette $17.64, $16.69 and $9.77.

**Standing.** FAILS. The Authority publishes ten years of it in the annual reports on its own site. The narrower true statement is that the January 2026 fees, rates and charges sheet does not carry a cost-per-enplanement figure and the Authority has not published a current-year one. Say that instead.

### D-064 · The comparison · Carried from v15 with the same defect

> the maintenance saving has never been demonstrated at all

**Where it was checked.** pdf 293 (printed B-107)

**What the record says.** 'The net savings were broken down into labor, contract, and lifecycle components. In collaboration with Authority operations management, a forecast of net savings by type and year was created. The full net savings are anticipated to be realized by 2030 ... The Authority plans to take steps to implement the TMP O&M savings and expects to achieve the annual dollar amounts shown in Exhibit D each year.'

**Standing.** FAILS, unchanged from the last pass. There is a method, set out at B-107 with a year-by-year forecast in Exhibit D, and it can be attacked on its merits, which is a better story than saying it does not exist. Cassotis has also answered the underlying charge on the record: the charge 'would have risen regardless of the new terminal, since the old landside terminal would have needed substantial renovations to continue operating.'

### D-065 · The comparison · New in this draft

> The building the board chose was sized for 13 to 15 million passengers a year.

**Where it was checked.** No record cited.

**What the record says.** The 13-to-15-million range appears only in the West Hills Gazette of Oct. 11, 2025. None of the three Official Statements states an annual design capacity. The Post-Gazette of Sept. 12, 2017 reports the opposite scale: 'While midfield was built as a hub capable of handling 32 million travelers a year, the new complex would be able to accommodate more than 18 million and could be expanded to serve as many as 25 million.' Trade coverage of the opening gives 'as many as 15 million annual passengers' as an upper bound, not a band.

**Standing.** FAILS as sourced. A single local outlet against the Post-Gazette's contemporaneous 18-to-25-million and against silence in every bond document. The whole under-use argument rests on this band, and the band is the weakest-sourced number in the story. Either find the design capacity in the master plan or the FAA submission, or build the argument on the gates: 51 from 75, which is in the 2017 clip and is a fact.

### D-066 · The comparison · New in this draft

> Pittsburgh boarded 9.95 million in 2024, which is between 31 and 51 percent below that band

**Where it was checked.** pdf 42 (printed 32); pdf 50 (printed 40)

**What the record says.** 'In 2024, total passengers of 9.95 million exceeded pre-pandemic 2019 by 2%, or about 170,000 passengers, which was the highest total the Airport has seen in nearly 20 years.' Enplaned passengers in 2024 were 4,964,361.

**Standing.** FAILS three ways, and it is the load-bearing sentence of the section. Pittsburgh did not board 9.95 million; it boarded 4,964,361. The 9.95 million is total passengers, arriving and departing, and the case's own standing rule is that enplanements and total passengers never appear in the same sentence, let alone as the same number. The percentages are computed on the wrong denominator: 9.95 against a 13-to-15 band is 23.5 to 33.7 percent below the band, while 31 and 51 percent is how much the band exceeds the actual. And the Authority's sentence containing that same 9.95 million calls it the highest total in nearly twenty years, which is the exact opposite of the use the draft puts it to. If the Authority reads one sentence in this story, it will be this one.

### D-068 · The comparison · New in this draft

> Roughly 11 cents of every dollar that paid for it is grant money. The rest was borrowed against what the airport can earn.

**Where it was checked.** pdf 19 (printed 9)

**What the record says.** Estimated funding sources for the TMP and ARP, total $1,928,820k: Bond Proceeds $1,583,275k; Federal AIP Grants $11,011k; Federal BIL ATP and AIG Grants $82,586k; Federal COVID-19 Relief Grants $20,412k; PFC pay-as-you-go $76,907k; CFC pay-as-you-go $62,827k; State Grants and Other $30,460k; Authority Funds $61,341k.

**Standing.** FAILS on both sentences. Federal grants are $114,009k, or 5.9 percent. Adding State Grants and Other, which the footnote says includes a Richard King Mellon Foundation grant, interest earnings and insurance proceeds, reaches 7.5 percent. Nothing reaches 11. And the rest was not all borrowed: bond proceeds are 82.1 percent, with passenger facility charges at 4.0 percent, customer facility charges at 3.3 percent and Authority funds at 3.2 percent. The Post-Gazette, on a narrower federal definition, put it at 4 percent.

### D-070 · The comparison · Carried from v15 with the same defect

> What it spends keeping the empty building standing has not been disclosed.

**Where it was checked.** pdf 293 (printed B-107)

**What the record says.** 'The Signatory Airlines and the Authority agreed to postpone the demolition of the existing landside building to reduce project costs and associated debt. The Authority estimates that it will incur $2,047,000 per year in incremental O&M Expenses as a result of not demolishing the existing terminal, which costs were netted against TMP O&M savings in Exhibit D.'

**Standing.** FAILS, unchanged from the last pass. It is disclosed at $2,047,000 a year in the same document the story quotes in the sentence before, and it is netted against the very savings the paragraph above says were never demonstrated. It also corrects the preceding sentence: the airlines agreed to the postponement with the Authority. Print the number.

### D-075 · Slots · New in this draft

> [THE TICKET COUNTER] ... Fraport Pittsburgh, the concessions operator suing over a terminated lease that ran to 2029, and Grant Oliver, the parking contractor since 1952, are both in the file and neither has been called.

**Where it was checked.** os-2025ab pdf 305 and pdf 59; os-2025ab pdf 301; os-2021ab pdf 283

**What the record says.** Fraport: 'In June 2022, the Authority terminated the Fourth Amended and Restated Master Lease ... Fraport filed a motion for injunctive relief ... On September 1, 2023, Fraport and the Authority reached a settlement of all disputes between them and entered into a Settlement Agreement.' And at pdf 59: 'in 2023 in professional services the Authority paid $10.5 million in litigation settlement of the previous concession operator Fraport.' Parking: 'LAZ Parking assumed operations of parking facilities on October 1, 2022. The contract extends to December 31, 2027.' The 2021 statement has Grant Oliver operating since 1992; the Post-Gazette of July 15, 2022 reports the company leaving 'after 70 years on the job.'

**Standing.** FAILS on both names, in a bracket that exists to say who has not been called. Fraport is not suing: it settled on Sept. 1, 2023, and the Authority paid $10.5 million, which is a fact the story does not have and probably wants. Grant Oliver is not the parking contractor: LAZ Parking has run it since Oct. 1, 2022. Both are still worth calling, for what they know rather than for what this bracket says they are.

## The 6 with no located source

### D-013 · Scene · New in this draft

> The airlines that will pay for the building had signed the agreement that made it possible and had sent no one to speak

**What was searched.** No attendance record located.

**Standing.** An absence claim about who was in a room. It needs the programme, or the reporter's own notes saying so. It is a good sentence and it is currently unsupported.

### D-033 · What it costs · Carried from v15 with the same defect

> "It is not a ticket fee charged to passengers," Bob Kerlik ... wrote in the airport's own publication in 2019

**What was searched.** Blue Sky News, 2019. Uncaptured and in no vault.

**Standing.** Still a direct quotation from an uncaptured page, flagged in the last pass and unchanged. Capture through Wayback and hash. Say that Blue Sky News is published by the Authority and edited by Kerlik, because the sentence is a spokesman defining a term in his own outlet.

### D-042 · What it costs · Carried from v15 with the same defect

> Studies of per-passenger taxes added at booking find carriers passing nearly all of it into ticket prices.

**What was searched.** No citation given, and the case deliberately excludes the 99 percent figure because it measures a ticket tax.

**Standing.** Unattributed, in a paragraph whose next sentence names authors, a journal and a year. Name one study for the tax side, or the asymmetry has a floor under only one of its two legs.

### D-059 · The comparison · Carried from v15 with the same defect

> Cassotis said that day that renovating "is actually not cheaper and we looked at it."

**What was searched.** The phrase appears in none of the seven captured Post-Gazette clips, in none of the eight hashed documents and in no quote row. The Sept. 12, 2017 clip carries the reporter's paraphrase instead: Cassotis 'considered other approaches, including renovations to the existing facilities and relocating the boarding terminal, but all proved to be more costly than replacing landside.'

**Standing.** Unchanged from the last pass and still the gravest item in the draft. The case's own apparatus records it as 'KDKA, Sept. 12, 2017, uncaptured' and calls it 'the sentence the whole options section rests on.' It sits under a section head that says the Authority never released the comparison, so a quotation attributed to a broadcast nobody has heard is carrying the section. Capture the KDKA segment, or use the paraphrase the Post-Gazette printed and attribute it to the Post-Gazette.

### D-061 · The comparison · Carried from v15 with the same defect

> The Authority's 2017 annual report says the plan is on file with the Federal Aviation Administration.

**What was searched.** The vault holds the 2021 annual report, not the 2017 one. Searching all eight hashed documents for the master plan returns references to the board's 2017 approval but nothing stating it is on file with the FAA.

**Standing.** Unchanged. The document this rests on is not in the case, and the story's last line rests on it too, so the frame closes on an uncaptured citation.

### D-072 · The comparison · Carried from v15 with the same defect

> Council did not hold one ... No elected body in Allegheny County has taken the question up since.

**What was searched.** No council record is in the case.

**Standing.** Unchanged. The first is settled by one Legistar search, which then becomes the citation. The second is an absence claim across eight years and every elected body, and needs a stated method: which bodies, which records, which years.

## Full ledger

### FAILS (21)

| ID | Section | Carry | Claim | Where checked | Note |
|---|---|---|---|---|---|
| D-001 | Headline | new | Pittsburgh built a $1.7 billion airport terminal. What it costs airlines to fly there has never been higher. | pdf 170 (printed 53), Table IV; pdf 62 (printed 52) | FAILS. The charge was higher in 2020, at $20.50 on the audited basis and $20.57 as the Authority reports it in the same statement. $16.10 is the highest since 2020 and the highest in a normal year, which is a true and printable sentence. 'Has never been higher' is not, and it is ... |
| D-003 | Dek | carried-broken | The gap is closed with casino and gas money the Authority decides on once a year and is under no obligation to provide. | pdf 316 (Exhibit E); pdf 32; pdf 67 (printed 57) | FAILS on all three clauses, and this is the same failure the last pass found in the last draft's dek. Gas is designated at zero in every forecast year, so the money closing the gap going forward is gaming, not 'casino and gas.' The deposit is monthly at discretion, not annual. An... |
| D-004 | Scene | new | PITTSBURGH (AP) — | - | FAILS, and it is the most immediately damaging error in the draft. An (AP) dateline attributes the story to the Associated Press. It is not an AP story. This appears to be an artifact of the v6 apparatus note, which used 'PITTSBURGH (AP)' as an illustration of a dateline the outl... |
| D-005 | Scene | new | On a morning in October ... a building that opened eight years after the board approved it | - | FAILS. The October morning was not the opening. The terminal opened on Nov. 18, 2025, five and a half weeks later, with a United arrival from San Francisco and a Southwest departure to Denver. The whole scene is written as opening day and the graf says so. Either move the scene t... |
| D-006 | Scene | new | no one from the congressional delegation that had been announcing federal checks for the project since 2021 had come out to the airfield tha... | - | FAILS as written. Four members of the delegation were there. The sentence's plain reading is that none came. If the intended point is that none of them criticised the project, say that, and name them: it is a stronger sentence with four names in it than with an absence. Note also... |
| D-015 | Nut | carried-broken | what the airport charges the airlines works out to $16.10 for every passenger they board, the highest figure in the airport's history | os-2025ab pdf 170; pdf 62 | FAILS three ways. It is not the highest in the airport's history. It is a fiscal 2025 figure in a story dated August 2026, when the Authority's own current-year expectation is $17.64. And it is on the federal-filing basis while the sentence beside it, and the $11.34 two grafs lat... |
| D-019 | Nut | new | Every estimate the Authority gave the public before it sold the bonds came in under what followed, and the gap has widened in every year sin... | os-2021ab pdf 185; os-2025ab pdf 62 | FAILS on both halves. The 2021 forecast overshot the 2021 actual, so not every estimate came in under what followed. And the gap does not widen in every year: it is negative in 2021 before turning positive and growing 2022 through 2024. The true version is that from 2022 onward e... |
| D-022 | Covenant | carried-broken | that account holds royalties from gas wells drilled on airport land and Pennsylvania's tax on slot machines ... It designated $19.1 million ... | pdf 316 (Exhibit E); pdf 61 (printed 51); pdf 295 | FAILS, and it is the same failure the last pass found. The $19.1 million and the $3 million were not gas and casino money. They were federal pandemic relief. The statement also gives two figures for 2023, $3,029k and $4,040k. And the Coverage Account is not where Other Pledged Re... |
| D-030 | Covenant | new | One survey of 57 United States airport bond documents put the share permitting this sort of transfer at 59 percent, naming Austin, Los Angel... | - | FAILS on three counts. The 59 percent is 30 of 51, not a share of 57. Los Angeles and San Francisco are not the airports the page names for this finding; Austin and Dallas Love Field are. And the source is not an undated consultant's compilation: it is a dated, self-declared AI-g... |
| D-037 | What it costs | carried-broken | KBRA, which rated the 2025 bonds A+, listed among the credit challenges that "a rising CPE could discourage service expansion or retention, ... | - | FAILS, unchanged from the last pass. The A+ is now right, which is a fix. The quotation marks are still around a paraphrase, and that is the exact defect the quote gate was built to catch and did catch in eight earlier rows. Obtain the presale or drop the quotation marks. |
| D-038 | What it costs | new | Spirit Airlines left Pittsburgh on May 1, 2026, and traffic fell 1.1 percent. | - | FAILS, and the placement makes it worse. Spirit did not leave Pittsburgh; Spirit stopped existing. Put in a paragraph about a rising charge discouraging low-cost carriers, the sentence implies Pittsburgh's cost drove the exit, which nothing supports. The date is May 2, not May 1.... |
| D-041 | What it costs | carried-broken | Thijs Koopmans and Rogier Lieshout, writing in the Journal of Air Transport Management in 2016 | Journal of Air Transport Management 53 (2016) 1-11, doi:10.1016/j.jairtraman.2015.12.013 | FAILS, unchanged from the last pass. Carl, not Thijs. The characterisation of the finding is exact, to the word, in both directions. One given name is all that stands between this and the best citation in the piece. |
| D-049 | 2028 | new | The Authority borrowed about $1.66 billion across three bond sales ... and owes about $2.5 billion in principal and interest by the time the... | pdf 39; pdf 147; pdf 1 of each vintage | FAILS. The $1.66 billion correctly includes the 2025 sale and the $2.5 billion does not, so the sentence pairs a three-sale principal with a two-sale debt-service total. Total principal and interest to 2056 is about $3.23 billion. Fixing it makes the sentence worse for the Author... |
| D-053 | The test | carried-broken | In 2025 passengers again beat the base case and the charge landed at $16.10, three cents above the slow-growth case | os-2021ab pdf 185 | FAILS on the first half, unchanged from the last pass. The 2025 enplanement actual has never been fixed and the only figure the case holds points the other way. The three-cent line pairs a federal filing against an Official Statement forecast, and on the Authority's own $16.69 th... |
| D-058 | The test | new | the Authority publishes no cost-per-enplanement figure on its own website | - | FAILS. The Authority publishes ten years of it in the annual reports on its own site. The narrower true statement is that the January 2026 fees, rates and charges sheet does not carry a cost-per-enplanement figure and the Authority has not published a current-year one. Say that i... |
| D-064 | The comparison | carried-broken | the maintenance saving has never been demonstrated at all | pdf 293 (printed B-107) | FAILS, unchanged from the last pass. There is a method, set out at B-107 with a year-by-year forecast in Exhibit D, and it can be attacked on its merits, which is a better story than saying it does not exist. Cassotis has also answered the underlying charge on the record: the cha... |
| D-065 | The comparison | new | The building the board chose was sized for 13 to 15 million passengers a year. | - | FAILS as sourced. A single local outlet against the Post-Gazette's contemporaneous 18-to-25-million and against silence in every bond document. The whole under-use argument rests on this band, and the band is the weakest-sourced number in the story. Either find the design capacit... |
| D-066 | The comparison | new | Pittsburgh boarded 9.95 million in 2024, which is between 31 and 51 percent below that band | pdf 42 (printed 32); pdf 50 (printed 40) | FAILS three ways, and it is the load-bearing sentence of the section. Pittsburgh did not board 9.95 million; it boarded 4,964,361. The 9.95 million is total passengers, arriving and departing, and the case's own standing rule is that enplanements and total passengers never appear... |
| D-068 | The comparison | new | Roughly 11 cents of every dollar that paid for it is grant money. The rest was borrowed against what the airport can earn. | pdf 19 (printed 9) | FAILS on both sentences. Federal grants are $114,009k, or 5.9 percent. Adding State Grants and Other, which the footnote says includes a Richard King Mellon Foundation grant, interest earnings and insurance proceeds, reaches 7.5 percent. Nothing reaches 11. And the rest was not a... |
| D-070 | The comparison | carried-broken | What it spends keeping the empty building standing has not been disclosed. | pdf 293 (printed B-107) | FAILS, unchanged from the last pass. It is disclosed at $2,047,000 a year in the same document the story quotes in the sentence before, and it is netted against the very savings the paragraph above says were never demonstrated. It also corrects the preceding sentence: the airline... |
| D-075 | Slots | new | [THE TICKET COUNTER] ... Fraport Pittsburgh, the concessions operator suing over a terminated lease that ran to 2029, and Grant Oliver, the ... | os-2025ab pdf 305 and pdf 59; os-2025ab pdf 301; os-2021ab pdf 283 | FAILS on both names, in a bracket that exists to say who has not been called. Fraport is not suing: it settled on Sept. 1, 2023, and the Authority paid $10.5 million, which is a fact the story does not have and probably wants. Grant Oliver is not the parking contractor: LAZ Parki... |

### UNSOURCED (6)

| ID | Section | Carry | Claim | Where checked | Note |
|---|---|---|---|---|---|
| D-013 | Scene | new | The airlines that will pay for the building had signed the agreement that made it possible and had sent no one to speak | - | An absence claim about who was in a room. It needs the programme, or the reporter's own notes saying so. It is a good sentence and it is currently unsupported. |
| D-033 | What it costs | carried-broken | "It is not a ticket fee charged to passengers," Bob Kerlik ... wrote in the airport's own publication in 2019 | - | Still a direct quotation from an uncaptured page, flagged in the last pass and unchanged. Capture through Wayback and hash. Say that Blue Sky News is published by the Authority and edited by Kerlik, because the sentence is a spokesman defining a term in his own outlet. |
| D-042 | What it costs | carried-broken | Studies of per-passenger taxes added at booking find carriers passing nearly all of it into ticket prices. | - | Unattributed, in a paragraph whose next sentence names authors, a journal and a year. Name one study for the tax side, or the asymmetry has a floor under only one of its two legs. |
| D-059 | The comparison | carried-broken | Cassotis said that day that renovating "is actually not cheaper and we looked at it." | - | Unchanged from the last pass and still the gravest item in the draft. The case's own apparatus records it as 'KDKA, Sept. 12, 2017, uncaptured' and calls it 'the sentence the whole options section rests on.' It sits under a section head that says the Authority never released the ... |
| D-061 | The comparison | carried-broken | The Authority's 2017 annual report says the plan is on file with the Federal Aviation Administration. | - | Unchanged. The document this rests on is not in the case, and the story's last line rests on it too, so the frame closes on an uncaptured citation. |
| D-072 | The comparison | carried-broken | Council did not hold one ... No elected body in Allegheny County has taken the question up since. | - | Unchanged. The first is settled by one Legistar search, which then becomes the citation. The second is an absence claim across eight years and every elected body, and needs a stated method: which bodies, which records, which years. |

### ATTENTION (30)

| ID | Section | Carry | Claim | Where checked | Note |
|---|---|---|---|---|---|
| D-002 | Dek | new | the airport falls short of its bond covenant in five of the next six years on the revenue actually pledged to the bonds | pdf 202 (printed B-16); covenant at pdf 34 | The arithmetic is exact. The words are the problem. The covenant as written includes the Coverage Account, so the airport does not fall short of its covenant on the covenant's own terms; it falls short of 125 percent on pledged Net Revenues alone, which is a test the reporter is ... |
| D-007 | Scene | new | under 811,000 square feet of new glass and steel | os-2025ab pdf 14 | Two figures, one from the bond document and one from a single local outlet. Both are usable; attribute whichever is used. Note that three of this draft's most distinctive scene details, the 811,000 square feet, the 13-to-15-million capacity band and the hundreds waiting outside, ... |
| D-008 | Scene | new | hundreds of people waiting outside for a look at a building most of them had watched rise from the parkway | - | If this is the reporter's own observation, say so and it stands. If it is the Gazette's, it is one outlet and the number is small against the 10,000 registrations the Authority reports. 'Most of them had watched it rise from the parkway' is not observable and not attributable. |
| D-009 | Scene | new | called the terminal a catalyst for the region's economic engine | - | The paraphrase drops the word the line was built on. At an airport, 'economic jet engine' is the joke; 'economic engine' is a press release. Quote it or leave it alone. |
| D-010 | Scene | new | $600 million above the figure the board approved | os-2025ab pdf 16, pdf 72, pdf 125 | The subtraction is right and the framing is not. The board approved successive increases and the airlines approved each one; $1.7 billion is itself an approved figure. And the $1.7 billion covers the Terminal Modernization Program and the Airside Renovation Program, a wider scope... |
| D-011 | Scene | new | Sara Innamorato ... put the project's economic impact at $2.5 billion and the jobs created during construction at 14,300. | - | The figures are in the account; the attribution of them to Innamorato is not. They read as the Authority's own impact study. Attribute them to whoever produced them, and say it is a projection, because an economic-impact number in a story about a cost overrun is the Authority's a... |
| D-012 | Scene | new | called it an airport built for Pittsburgh, by Pittsburgh | - | She said it, in the Authority's own release, on Nov. 18. She is not on record saying it at the October ceremony. As placed, the draft puts a November quotation in an October scene. Quote it with its date, or move the scene. |
| D-016 | Nut | new | A single narrow-body jet leaving Pittsburgh with 175 people aboard carries about $2,800 in airport charges ... In 2019 ... about $1,800. By ... | pdf 202 for 2030; pdf 170 and pdf 62 for 2019 | The arithmetic reproduces and the device works. Three things to fix. It is the reporter's multiplication and is not labelled as such. The 2019 leg uses the budgeted $10.35 rather than the audited $9.77, which is the difference between about $1,800 and about $1,700, and the basis ... |
| D-017 | Nut | new | In 2019, the last year the airport owed nothing on a terminal | pdf 170, Table IV, debt service row | Backwards as written. Table IV shows the airport paying $21.2 million of debt service in 2019 and nothing in 2020 through 2023, so 2019 is the last year it DID owe, and the years it owed nothing come after. The intended point, that 2019 is the last clean year before the modernisa... |
| D-018 | Nut | carried-broken | Cassotis said in 2017 ... that the charge would fall to $9.73 by 2023; it was $11.34. | Post-Gazette Sept. 12, 2017; os-2025ab pdf 62 and pdf 170 | Still carrying the omission the last pass flagged. '(in today's dollars)' means 2017 dollars, and the draft scores the promise against a nominal 2023 figure. And the statement prints two different 2023 actuals, $11.34 and $11.50; the case rule on a self-contradicting document is ... |
| D-020 | Covenant | carried-ok | The Authority promised its lenders that the airport would earn at least 125 percent of what it owes them each year, and that promise is the ... | pdf 34 | The plain-English rendering is good and keeps the banned word out. It is not the one test: there are two limbs and the 125 percent limb is the second. Saying 'the promise the financing turns on' keeps the force and loses the overstatement. Worth knowing that limb (a), on Net Reve... |
| D-027 | Covenant | new | Footnote 2 of the same statement says the coverage calculation was not applicable from 2020 through 2023 because interest was capitalized an... | pdf 61 (printed 51) | The footnote says no debt service was due. It does not give capitalised interest as the reason; the capitalisation dates are stated elsewhere, at pdf 39 and in the forecast notes. Attribute the reason separately or drop it. The caution itself is well placed and does the draft cre... |
| D-029 | Covenant | carried-ok | Gaming money has been flat at $12.4 million a year since 2020 ... "to reduce or eliminate payments." Gas royalties ran between $5.56 million... | pdf 67-68 (printed 57-58) | Figures and quotations exact, and the range is now given to the cent, which is an improvement on the last draft. The omission from the last pass is still open: the same paragraph says that in exchange for the deductions 'CNX made certain commitments to increase drilling operation... |
| D-034 | What it costs | new | At $16.10, Pittsburgh is the fifth most expensive of 32 medium hubs | - | A real improvement on the last draft, which never told the reader Pittsburgh is a medium hub. The rank itself is still C-grade and none of the underlying filings has been pulled. |
| D-035 | What it costs | carried-ok | costs an airline more per boarded passenger than Atlanta, Charlotte, Denver ... Atlanta boards 53 million passengers a year at $4.48. | FY2025 large-hub table | Every one of the sixteen holds on the compiler's numbers. Still C-grade and still unpulled. Denver is thirty cents below, which is inside any basis difference. The head above this section says 'more than at any of 16 large hubs,' which reads as all large hubs rather than these si... |
| D-036 | What it costs | carried-broken | Kansas City opened a comparable single terminal in February 2023, into a market of about the same size ... Its charge was $15.37 in fiscal 2... | - | The figures reproduce and the shape of the comparison is real: Kansas City comes back down and Pittsburgh does not. Three fixes. 'About the same size' is generous; Kansas City boarded about 22 percent more in 2024 and ranks eight places higher. The Kansas City forecast is from a ... |
| D-039 | What it costs | carried-broken | Low-cost and ultra-low-cost carriers flew 29.7 percent of Pittsburgh's departing passengers in 2014 and 44.3 percent in 2024. | derived in 02-data/airline-mix.csv from the carrier tables | Reproduces, and is still the reporter's derivation rather than a printed figure, still unlabelled. Name the carriers counted as low-cost: the classification is the entire result, and moving Southwest in or out swings it by twenty-five points. |
| D-040 | What it costs | carried-ok | Seth Lehman, a senior director at Fitch Ratings, told the Bond Buyer in April 2025 ... "above what is standard for an A-rated airport." | Bond Buyer, April 21, 2025, by Christina Baker | Quote verbatim. The title is the draft's, not the paper's. Source it to Fitch or use the paper's word. Capture and hash the clip. |
| D-044 | What it costs | new | Parking was restructured when the terminal opened. | pdf 301 (printed B-115) | True and far too thin for a sentence in a paragraph about who pays. The restructuring raised the cheapest walk-to-terminal option out of existence and split every product into advance and drive-up rates. Give the before and after, or cut it: as written it asserts a change without... |
| D-045 | What it costs | carried-ok | Pennsylvania taxpayers pay through a $12.4 million appropriation of gambling money that goes to the airport instead of somewhere else. | pdf 66-67 (printed 56-57) | The appropriation and the statutory route are solid. 'Instead of somewhere else' is a claim about the counterfactual that the Gaming Act's distribution formula would have to establish. Show where the money would otherwise go, or drop the clause. |
| D-046 | 2028 | new | Eleven signatory carriers hold about 97.8 percent of the airport's 2024 market share. | pdf 70 (printed 60); pdf 195; pdf 121 | Eleven is right on the body of the statement and the count is contradicted at pdf 121, which lists ten. Note also that one of the eleven, Spirit, ceased operating in May 2026, so 'hold' in the present tense is already out of date in a story published in August 2026. |
| D-054 | The test | carried-ok | Between its 2021 and 2023 bond statements the Authority carried the passenger forecast forward unchanged and raised the forecast cost 23.6 p... | os-2021ab pdf 185; os-2023abc pdf 208 (printed B-16) | 'Carried forward unchanged' is exact, digit for digit, and is the strongest single finding in this section. The 23.6 percent is a mean of four annual revisions computed by the reporter and still not labelled as computed. Giving the range instead, 19.8 to 27.4 percent, needs no la... |
| D-055 | The test | carried-ok | Cassotis said the charge would fall from $12.69 to $9.73 by 2023. Kerlik said the project would use "no local tax dollars" ... Sprys said th... | - | The quotations are exact. Two attributions are not. Bowes is manager of corporate real estate, not American's representative in Pittsburgh, and in the clip he is talking about the project's costs and open questions generally, with the preceding paragraph having him say the saving... |
| D-056 | The test | carried-ok | The document the Authority filed with investors eight weeks before Sprys spoke had already put the opening year at $12.92 in the base case a... | pdf 185 (printed B-19); pdf 1 | Figures exact. Sixty-four days is nine weeks and one day, not eight. And 'the opening year' is the reporter's gloss: the column is 2025 and the terminal opened in November 2025, which happens to work, but the 2021 statement projected delivery for late 2024 or early 2025. Say 2025... |
| D-060 | The comparison | carried-ok | Federal guidance ... requires that comparison, weighing each option against "a wide range of evaluation criteria, including its operational,... | AC 150/5070-6B, section 202.b.7); chapter 9 | Quote verbatim and correctly located. 'Requires' is the word to test: an Advisory Circular is guidance, and its force comes from grant assurances and FAA acceptance of a federally funded master plan. Establish that this plan was FAA-funded or accepted, or soften the verb. |
| D-062 | The comparison | carried-broken | Neither the Authority nor the FAA has released it, and no estimate for renovating the old terminal has appeared in the nine years since. | - | Unchanged. A negative claim of this weight needs the record of the attempt: a Right-to-Know to the Authority and a FOIA to the FAA, with dates, and a sentence saying what was asked and what came back. |
| D-067 | The comparison | new | short of the level the airport last saw before US Airways closed its connecting hub in December 2004 | pdf 13; pdf 44; pdf 177 | The substance holds: 2024 total passengers are below the pre-de-hubbing level. December 2004 is a announcement date and the drawdown ran across several years, and the Authority's own statement gives two different de-hubbing years. Say 2004 without the month, or say what happened ... |
| D-071 | The comparison | carried-broken | In February 2018, four months after the board approved the project, John Fiorita, who had run US Airways' properties and facilities in Pitts... | - | Five months and eight days, not four. And the title is still inflated; use the paper's words. Flagged last pass, unchanged. |
| D-073 | The comparison | carried-broken | on July 8 it seated state Sen. Devlin Robinson, R-37th, on a 12-3 vote | TribLive, July 8, 2026 | Tally confirmed. The date is probably a day out, and the year is missing from a sentence that in an August 2026 story could read as either year. Check the council minutes. Cutting the three no votes, as the draft's own TK contemplates, also removes the sentence that needed three ... |
| D-074 | The comparison | carried-broken | Tasso Katselas, who designed the terminal Pittsburgh replaced and whose work the new building supersedes | Post-Gazette, June 24, 2021 | 'Part of which' is the qualifier, and this draft doubles the overstatement by adding 'whose work the new building supersedes.' The airside he designed is still in service; the landside is what closed. |

### VERIFIED (19)

| ID | Section | Carry | Claim | Where checked | Note |
|---|---|---|---|---|---|
| D-014 | Scene | new | Christina Cassotis, who has run the Allegheny County Airport Authority since 2015 | pdf 42 (printed 32) | Year confirmed in the Authority's own statement. No month is given there; if a month is wanted, source it separately. |
| D-021 | Covenant | carried-ok | shows the airport falling below it in five of the six years from 2026 through 2030 on the revenue actually pledged to the bonds | pdf 202 (printed B-16) | Reproduces exactly. Keep the 'analyzed by' label the last draft carried; this draft drops it here and puts it only in the plate note and the tagline. |
| D-023 | Covenant | new | In the 2021 forecast, six of eight computable years fall below on the same basis, two of four in the strong-recovery case and four of four i... | os-2021ab pdf 185 (printed B-19); os-2025ab pdf 202 (printed B-16) | Every number reproduces from the printed rows. This is the best-built passage in the draft. |
| D-024 | Covenant | new | Recomputing the combined column from the same rows reproduces every printed ratio to within rounding [plate note] | - | Fourteen of fourteen reproduce. The check is sound and the plate is right to state it, because it is what proves the reporter is reading the table the way the consultant built it. |
| D-025 | Covenant | new | The Coverage Account sits ninth in the flow of funds ... It is capped at 25 percent of the year's debt payment. The forecast assumes that ce... | os-2025ab pdf 32, pdf 34, pdf 202; os-2021ab pdf 185 | Reproduces exactly, and the two exceptions are worth a clause: the 2021 slow case in 2025 and the 2025 statement in 2027. This is the arithmetic that carries the section. |
| D-026 | Covenant | new | The gap the 2025 forecast leaves runs $5.6 million to $11.7 million a year, against $0.5 million to $5.1 million in the 2021 forecast. [plat... | - | Both ranges exact to the thousand. The plate's decision to keep the panels adjacent and unjoined, because no document says this designated revenue closes this gap, is the right call and should be said in the prose too, not only on the plate. |
| D-028 | Covenant | new | the Coverage Account contribution the 2025 statement prints for 2026 is $21.2 million, which matches neither the designated series nor the $... | pdf 202 (printed B-16); pdf 67 (printed 57); pdf 316 | Correct, and the reason is now visible: the Coverage Amount is 25 percent of that year's aggregate debt service and is fed from Revenues, while the $11.575m is a designation into Other Pledged Revenues, which sits in Net Revenues. Two different mechanisms. Naming that turns the c... |
| D-031 | Covenant | new | Missing the covenant in a single year is not a default. The indenture requires the Authority to hire a consultant, take its advice and raise... | pdf 34-35 | Accurate to the instrument, correctly placed as a refutation, and the strongest version of this paragraph the drafts have carried. Keep it exactly as it is. |
| D-032 | What it costs | carried-ok | $298.36 per square foot of terminal space and $4.06 per 1,000 pounds of landing weight as of January | pdf 2 | Gated in the case at q-006. Confirm the $4.06 landing fee in the harness run. |
| D-043 | What it costs | carried-ok | A $4.50 charge sits on every eligible ticket and did not come down when the terminal opened. Rental customers have paid $8 a day since Jan. ... | pfc notice pdf 2; os-2025ab pdf 66 | Both confirmed. The Post-Gazette's point still belongs in the sentence: the $4.50 'is federally capped at $4.50 per enplaned passenger for nearly every airport in the country,' so it did not come down because it could not. |
| D-047 | 2028 | carried-ok | The Airline Operating Agreements took effect Jan. 1, 2020 and expire Dec. 31, 2028, extendable three years only by mutual agreement. | pdf 70; pdf 82; pdf 195 | Exact. |
| D-048 | 2028 | carried-ok | In January 2025 the airlines voted ... to commit no less than $8.8 million ... for 2025 and $11.575 million a year for 2026 through 2028. Th... | pdf 67 (printed 57); pdf 71; pdf 281; pdf 295 | Both confirmed. The same statement says at pdf 72 that the Authority committed those amounts 'to pay debt service,' which is the contradiction the bracketed right-of-reply block already asks about. Worth carrying the majority-in-interest definition at pdf 195: signatory airlines ... |
| D-050 | 2028 | new | Twenty-eight of those years fall after the date on which every arrangement holding the current arithmetic together expires. | pdf 39 | Exact. |
| D-051 | The test | carried-ok | The 2021 forecast projected 4,924,000 boardings for 2024 if traffic recovered strongly and 4,369,000 if it recovered slowly. The year came i... | os-2021ab pdf 185; os-2025ab pdf 50 (printed 40) | Exact. The subtraction in the section head, 40,361, is the reporter's and should carry a label somewhere in the piece. |
| D-052 | The test | new | the same forecast put 2024 at $9.83 a passenger, and the year came in at $11.56, 17.6 percent high | os-2021ab pdf 185; os-2025ab pdf 62 | Both figures on the Authority's residual basis, so the comparison is like for like, and the percentage reproduces. The percentage is computed by the reporter and is not labelled. |
| D-057 | The test | carried-ok | The statement filed for investors in April 2025 forecasts $19.13. The Authority told the Post-Gazette it expects $17.64. | os-2025ab pdf 202; Post-Gazette Jan. 11, 2026 | Both confirmed, and the January article is captured and hashed in the media sibling, which repairs the case record: cpe-2026-claims.csv still says the article could not be read. The paper attributes $17.64 to 'the airport,' not to a named official. This draft has dropped the mont... |
| D-063 | The comparison | carried-ok | setting roughly $23 million a year of avoided upkeep against roughly $75 million a year of debt service on what was then a $1.1 billion proj... | Allegheny Institute, Oct. 4, 2017; os-2025ab pdf 202 | Confirmed, and the hedge this draft adds, 'larger than the figure the Institute used,' is the right response to the two-figures problem the draft flags in its own bracket. Worth saying the $23 million is the Authority's own estimate, which the Institute took at face value, and th... |
| D-069 | The comparison | carried-ok | The line for demolishing it read $33 million in the bond statement the Authority sold in 2023 and $0 in the one it sold in April 2025. | os-2023abc pdf 18; os-2025ab pdf 16 (printed 6) | Exact in both vintages, and the two totals give the $1.57bn to $1.70bn move in the same tables. |
| D-077 | Slots | new | [FACT-CHECK: two debt-service figures in the file. The coverage board carries $111.3 million a year from 2027. The 2024 audited annual repor... | pdf 202 (printed B-16); pdf 147 | The bracket is right to flag it and the answer is in hand. The two figures differ because the sealed sibling's range predates the April 2025 issuance, and because the forecast prints debt service both gross and net of PFCs Available for Debt Service. Resolve it as vintage plus ba... |

### SLOT (1)

| ID | Section | Carry | Claim | Where checked | Note |
|---|---|---|---|---|---|
| D-076 | Slots | carried-ok | [AUTHORITY RESPONSE: six questions sent [date], 72-hour hold ...] | - | Unsent. Nobody in this case has been contacted by anyone. The sixth question, what the Authority spends maintaining the closed terminal, is answered at $2,047,000 a year at pdf 293 and should be replaced. Add: on what basis does the Authority publish its cost per enplaned passeng... |

## Sources cited in this check

| ID | Tier | Source | Link | Vault copy | SHA-256 |
|---|---|---|---|---|---|
| `acaa-financials` | B | ACAA Reports & Financials page, annual financial reports 2015-2025 (each carrying Table IV, Rates and Cost Per Enplaned Passenger) | [link](https://flypittsburgh.com/acaa-corporate/newsroom/reports-financials/) | not in vault | - |
| `acaa-open-20251118` | B | ACAA opening-day release, Nov. 18, 2025, 'Transformed Pittsburgh International Airport Opens Today' | [link](https://www.prnewswire.com/news-releases/transformed-pittsburgh-international-airport-opens-today-302618557.html) | not in vault | - |
| `ai-20171004` | D | Allegheny Institute, Oct. 4, 2017, "Will Airport Reconfiguration Justify the $1.1 Billion Cost?" | [link](https://www.alleghenyinstitute.org/will-airport-reconfiguration-justify-1-1-billion-cost/) | not in vault | - |
| `blueskypit-spirit` | D | Blue Sky News, May 4, 2026, 'Spirit Ceases Operations: What It Means for Pittsburgh' (published by the Authority) | [link](https://blueskypit.com/spirit-ceases-operations-what-it-means-for-pittsburgh/) | not in vault | - |
| `bondbuyer-20250421` | C | Bond Buyer, April 21, 2025, Christina Baker, “Pittsburgh airport's bonds will ease the landing of its renovation” | [link](https://www.bondbuyer.com/news/pittsburgh-airports-bonds-will-ease-the-landing-of-its-renovation) | not in vault | - |
| `dwu-cpe` | C | DWU Consulting, Cost per Enplanement by Airport (compiler over FAA CATS Form 5100-127) | [link](https://dwuconsulting.com/info/data/cpe) | not in vault | - |
| `dwu-mci` | C | DWU Consulting, MCI airport page | [link](https://dwuconsulting.com/airports/MCI) | not in vault | - |
| `dwu-ratecov` | D | DWU Consulting, 'Rate Covenant Compliance' (a self-described DWU AI Product, published Apr. 20 2026, updated May 2 2026) | [link](https://dwuconsulting.com/airport-finance/articles/rate-covenant-compliance) | not in vault | - |
| `faa-ac-5070-6b` | A | FAA Advisory Circular 150/5070-6B, Airport Master Plans (with changes 1 and 2) | [link](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_150_5070-6B_with_chg_1&2.pdf) | not in vault | - |
| `faa-cats-127` | B | FAA CATS Form 5100-127, PIT, FY2025 (line 1.7) | [link](https://cats.airports.faa.gov/) | not in vault | - |
| `faa-cy2024` | A | FAA CY2024 commercial service enplanements | [link](https://www.faa.gov/airports/planning_capacity/passenger_allcargo_stats/passenger/arp-cy2024-commercial-service-enplanements.pdf) | not in vault | - |
| `fees-rates-2026` | A | PIT fees, rates and charges (January 2026) | [link](https://flypittsburgh.com/wp-content/uploads/2026/01/Fees-Rates-and-Charges-Trifold_January-2026.pdf) | `01-sources-archive/raw/fees-rates-2026.pdf` | `5234016fbf6e13df...` |
| `flykc-open` | B | Kansas City Aviation Department, new 40-gate terminal opening | [link](https://flykc.com/newsroom/news-releases/new-40-gate-terminal-at-kansas-city-international-airport) | not in vault | - |
| `kbra-20250401` | B | KBRA rating release, April 1, 2025, ACAA Series 2025A/B (A+, stable) | [link](https://www.kbra.com/publications/nCMpwPwM/) | not in vault | - |
| `koopmans-lieshout-2016` | A | Koopmans, C.C., & Lieshout, R. (2016). Airline cost changes: To what extent are they passed through to the passenger? Journal of Air Transport Management, 53, 1-11. | [link](https://doi.org/10.1016/j.jairtraman.2015.12.013) | not in vault | - |
| `os-2021ab` | A | ACAA Official Statement, Series 2021A/B (dated Aug. 11, 2021) | [link](https://web.archive.org/web/20251204144924id_/http://dwuconsulting.com/images/OS/PIT%202021AB%20OS.pdf) | `01-sources-archive/raw/os-2021ab.pdf` | `8da587b3e2ac5241...` |
| `os-2023abc` | A | ACAA Official Statement, Series 2023A/B/C (dated Oct. 12, 2023) | [link](https://emma.msrb.org/P21736898-P21334055-P21768100.pdf) | `01-sources-archive/raw/os-2023abc.pdf` | `2fb9c2c103aea517...` |
| `os-2025ab` | A | ACAA Official Statement, Series 2025A/B (dated April 22, 2025) | [link](https://web.archive.org/web/20251213065401id_/https://dwuconsulting.com/images/OS/PIT%202025AB%20OS.pdf) | `01-sources-archive/raw/os-2025ab.pdf` | `885183dbe4e2b48a...` |
| `pfc-amend-notice-2026` | A | ACAA public notice, amend PFC applications #4-#7 (May 2026) | [link](https://flypittsburgh.com/wp-content/uploads/2026/05/PIT-PFC-4-5-6-7-Amendment-Public-Notice.pdf) | `01-sources-archive/raw/pfc-amend-notice-2026.pdf` | `4f34d43c2822901e...` |
| `ppg-201709120131` | C | Post-Gazette, Sept. 12, 2017, "$1.1B approved for reconfiguration of Pittsburgh International" | [link](http://web.archive.org/web/20260115100640/https://www.post-gazette.com/business/development/2017/09/12/Pittsburgh-International-Airport-Allegheny-County-Authority-board-vote-plan-new-landside-terminal/stories/201709120131) | `../pit-tier1-media-archive/01-sources-archive/raw/ppg/ppg-201709120131.html` | `d0aa2320c7e0c4ef...` |
| `ppg-201802200035` | C | Post-Gazette, Feb. 20, 2018, "Critics call for more transparency" | [link](http://web.archive.org/web/20260110165254/https://www.post-gazette.com/business/development/2018/02/20/pittsburgh-international-airport-1-1-billion-dollars-modernization-critics/stories/201802200035) | `../pit-tier1-media-archive/01-sources-archive/raw/ppg/ppg-201802200035.html` | `8ca8a7c1911e9934...` |
| `ppg-202106240135` | C | Post-Gazette, June 24, 2021, airlines clear $1.4 billion plan | [link](http://web.archive.org/web/20260111072417/https://www.post-gazette.com/business/development/2021/06/24/1-4-billion-pittsburgh-international-airport-modernization-authority-landside-building-findlay/stories/202106240135) | `../pit-tier1-media-archive/01-sources-archive/raw/ppg/ppg-202106240135.html` | - |
| `ppg-202110140188` | C | Post-Gazette, Oct. 14, 2021, groundbreaking | [link](http://web.archive.org/web/20260415225740/https://www.post-gazette.com/business/development/2021/10/14/Pittsburgh-International-Airport-1-4-billion-terminal-modernization-midfield-Christina-Cassotis-Rich-Fitzgerald-Tasso-Katselas/stories/202110140188) | `../pit-tier1-media-archive/01-sources-archive/raw/ppg/ppg-202110140188.html` | - |
| `ppg-20220715` | C | Post-Gazette, July 15, 2022, Grant Oliver replaced by LAZ Parking after 70 years | [link](https://www.post-gazette.com/business/development/2022/07/15/pittsburgh-international-airport-grant-oliver-corporation-laz-parking-allegheny-county-airport-authority-christina-cassotis-merrill-stabile/stories/202207150125) | not in vault | - |
| `ppg-202512220055` | C | Post-Gazette, Jan. 11, 2026, "new terminal cost hundreds of millions more than expected" | [link](http://web.archive.org/web/20260725120336/https://www.post-gazette.com/news/transportation/2026/01/11/pittsburgh-international-airport-new-terminal-budget/stories/202512220055) | `../pit-tier1-media-archive/01-sources-archive/raw/ppg/ppg-202512220055.html` | `2d96cf8afed546c4...` |
| `trib-20260708` | C | TribLive, July 8, 2026, “Allegheny County Council approves 3 new members for airport authority” | [link](https://community.triblive.com/news/4089712) | not in vault | - |
| `whg-20251011` | C | West Hills Gazette, Oct. 11, 2025, "Pittsburgh Airport cuts ribbon on $1.75 billion terminal" | [link](https://westhillsgazette.com/pittsburgh-airport-cuts-ribbon-on-1-75-billion-terminal/) | not in vault | - |
| `wpxi-traffic-2026` | C | WPXI, Aug. 14, 2026, Pittsburgh International traffic slips after a carrier's exit | [link](https://www.wpxi.com/news/local/pittsburgh-international-airport-traffic-slips-one-carriers-exit-leaves-void/W2ZMQAH55JC5XPGZIH3KEES2K4/) | not in vault | - |
