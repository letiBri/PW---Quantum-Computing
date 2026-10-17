# Sector scouting with patent data — Quantum computing

**Project Work · Innovation Management · A.Y. 2026/27 · Politecnico di Torino**

| | |
|---|---|
| **Team** | 30 |
| **Sector** | Quantum computing |
| **Client** | Dell |
| **Data** | PATSTAT Global, via the EPO Technology Intelligence Platform (TIP) |
| **Unit of analysis** | DOCDB patent family |
| **Observation window** | 2000–2022, by earliest priority year |

---

## The commission

We act as analysts at an investment bank. Dell, an established client, wants a
picture of the quantum computing sector before deciding whether to acquire or
partner with anyone in it. The brief reduces to three questions:

1. How is the sector doing overall?
2. Which segments are growing, and which are fading?
3. Who are the emerging players worth approaching?

Our evidence is patent data. Firms file patents years before products reach the
market, so the patent record is a leading indicator of where R&D money has
already been committed — which is precisely what a buyer wants to see before the
revenue exists.

---

## Repository layout

```
.
├── config/
│   └── sector.yaml          every parameter of the dataset: codes, keywords, years
├── notebooks/               exploration and the Step 1 analysis as run on TIP
├── src/                     the pipeline, as it is refactored out of the notebooks
├── outputs/
│   ├── figures/             figures referenced by the deck
│   └── tables/              result tables
├── docs/
│   ├── methodology.md       choices that need defending, and why we made them
│   └── validation.md        the Step 0 validation protocol and its results
├── tests/
├── requirements.txt
└── README.md
```

Two rules govern what goes in here, both from the project brief. **Configuration,
not hard-coding**: the sector boundary lives in `config/sector.yaml` and nowhere
else, so that changing it is a one-file edit rather than a search across the
analysis. **Queries, not bulk data**: no PATSTAT extract is committed. What is
committed is the code that reproduces one, plus the small aggregate tables the
figures are drawn from.

---

## Defining the sector

A patent family belongs to the sector if it matches our CPC codes **or** carries
one of our keywords in a title or abstract:

$$\text{Quantum} = \text{CPC} \cup \text{Keywords}$$

CPC codes were chosen by reading the official scheme definitions rather than the
class titles. The core is `G06N10`, titled *"Quantum computing, i.e. information
processing based on quantum-mechanical phenomena"*, together with its five
subgroups — models, physical realisations, algorithms, error correction and
programming. To these we add two enabling-hardware classes, `B82Y10/00` and
`H10N60/12`, and two quantum-communication classes, `H04B10/70` and `H04L9/0852`.

Keywords are deliberately multi-word or technically specific. The bare term
*quantum* is useless for this sector: quantum dot, quantum well and quantum
efficiency are optoelectronics vocabulary and would flood the dataset with LED
and photovoltaic patents. Terms such as `transmon` earn their place differently —
they name a dominant qubit design precisely enough that no classification code is
needed to recognise it.

### What the two branches contribute

Run on PROD over 2000–2022, at family level:

| Branch | Families | Share of union |
|---|---:|---:|
| CPC | 46,932 | 93.4% |
| Keywords | 11,599 | 23.1% |
| — also found by CPC | 8,292 | |
| — **keyword-only** | 3,307 | 6.6% |
| **Union (the sector)** | **50,239** | 100% |

Two things follow. First, **71.5% of keyword hits are independently confirmed by
a classification code**, which is the signature of a keyword list that is not
over-reaching — a runaway list would produce a large branch mostly disjoint from
CPC. Second, **3,307 families are visible only in text**. Quantum computing is
well institutionalised in the CPC scheme, but roughly one family in fifteen still
escapes it, and those are the families a classification-only study would miss.

---

## Methodological choices

These apply to every number in the analysis and are stated here so that no figure
has to be defended twice.

**The DOCDB family is the unit of analysis.** A patent is valid only where it is
granted, so an applicant seeking protection in several countries files the same
invention several times, and each filing becomes a separate application. PATSTAT
links them under one `docdb_family_id`. Counting families counts inventions;
counting applications counts filings. Our largest family contains 98 applications
for a single 2002 invention — counted once at family level, 98 times at
application level. Both levels are reported side by side, because the gap between
them is itself a measure of how widely applicants seek protection.

**Time is the earliest priority year**, the first filing of an invention anywhere
in the world, which is the date closest to the act of inventing. Applications are
dated by their own filing year.

**The window closes at 2022.** Applications publish roughly 18 months after
priority and reach PATSTAT later still, so recent priority years are structurally
incomplete. Rather than plotting incomplete years and shading them, we end the
series at the last year treated as complete. A decline in the final years of a raw
PATSTAT series is an artefact of publication lag, not a fall in inventive
activity, and closing the window removes any chance of reading one for the other.

**Fractional counting.** A family in four CPC subclasses contributes ¼ to each; a
family with applicants from three countries splits among them. Every breakdown
therefore sums to the number of families rather than inflating it.

---

## What we have found so far

**The sector grows roughly twice as fast as patenting overall.** At family level,
quantum computing compounds at 6.17% a year over 2000–2022 against 4.46% for all
patents. Over 2010–2022 the gap widens to 11.94% against 6.24% — the field changed
gear in the 2010s rather than simply rising with the tide. The result holds at
application level and on both base years, so it does not depend on a choice we
made.

**It remains very small.** 1,065 families in 2000 and 3,974 in 2022, against
914,442 and 2,389,730 for world patenting — from 0.12% to 0.17% of all families.
Its share grew by a factor of 1.4, which is real, but the sector is still under
two families per thousand. Growth figures quoted without that base would badly
mis-size the opportunity.

**Quantum inventions are protected unusually widely.** Dividing applications by
families gives 2.30 jurisdictions per quantum invention in 2022, against 1.47 for
patents generally — about 56% more. Applicants are paying substantially more to
protect these inventions internationally, which is a revealed-preference signal of
expected value and a sector-level analogue of the Globalization indicator used in
Step 3.

---

## Status

| Step | Content | State |
|---|---|---|
| 0 | Sector definition, extraction, cleaning | Query built and counted; **validation outstanding** |
| 1 | General description: volume, growth, technology mix, geography | Volume and growth complete; technology mix and geography in progress |
| 2 | Competitive landscape: concentration, entrants, subfields, PEST | Not started |
| 3 | Present score: influence, volume, success, globalization | Not started |
| 4 | Future score: our own algorithm | Not started |
| 5 | Magic Quadrant | Not started |
| 6 | Strategic analysis and recommendation | Not started |

Two items are known gaps rather than work merely not yet reached.

**The query is not yet validated.** Reading the CPC scheme to choose codes is
construction, not validation: it justifies the codes but produces no evidence
about what the resulting set actually contains. The protocol is set out in
`docs/validation.md` — a stratified hand-labelled sample, drawn from the branches
that can actually be wrong rather than uniformly from the union.

**The scope boundary needs settling.** Including `H04B10/70` and `H04L9/0852`
makes this a quantum *technologies* study rather than a quantum *computing* one.
Quantum key distribution is heavily patented and geographically concentrated, so
the decision will show up in the applicant-country figures. The CPC subclass mix
in Step 1 will quantify how much of the dataset it accounts for, after which we
either justify keeping it or cut it. Either is defensible; leaving it unstated is
not.

---

## Reproducing the analysis

The analysis runs on the EPO Technology Intelligence Platform, which provides
authenticated access to PATSTAT. It cannot be run from a local machine without a
TIP account.

```bash
git clone https://github.com/letiBri/PW---Quantum-Computing.git
```

Upload the repository to TIP, open `notebooks/`, and run the Step 1 notebook top
to bottom. Develop against `ENV = "TEST"` (a ~10K-publication sample, fast enough
to iterate on) and switch to `ENV = "PROD"` for any number that will be reported.
The two differ only by that constant.

Expensive queries are cached to `outputs/` on first run and read from disk
afterwards, so a lost kernel costs seconds rather than a working session. Delete
the cache files to force recomputation.

---

## Team 30

| Matricola | Name |
|---|---|
| 358251 | Almarua Amirtay |
| 354966 | Letizia Brizzi |
| 355188 | Leonardo Passeri |
| 358334 | Prince Thekkedath |
| 353302 | Michal Kruszewski |

### Contribution statement

*To be completed before submission: who did what, per the project brief.*

### Use of generative AI

*To be completed and reviewed by the team before submission.* Generative AI was
used during development as a programming and writing aid — among other things for
drafting and reviewing notebook code, checking CPC class definitions against the
official scheme, and drafting repository documentation. All analytical choices,
all queries run against PATSTAT, and all results reported are the team's own, and
every figure in the deck was produced by code in this repository.

---

## References

Sector definition and classification

- Cooperative Patent Classification scheme — https://www.cooperativepatentclassification.org
- PATSTAT Global data catalogue, EPO

Indicators used from Step 3 onward

- Hall, B. H., Jaffe, A. B., & Trajtenberg, M. (2001). *The NBER patent citation data file* (NBER Working Paper No. 8498).
- Hall, B. H., Jaffe, A., & Trajtenberg, M. (2005). Market value and patent citations. *RAND Journal of Economics*, 36(1), 16–38.
- Ernst, H. (1998). Patent portfolios for strategic R&D planning. *Journal of Engineering and Technology Management*, 15(4), 279–308.
- Guellec, D., & van Pottelsberghe de la Potterie, B. (2000). Applications, grants and the value of patent. *Economics Letters*, 69(1), 109–114.
- Harhoff, D., Scherer, F. M., & Vopel, K. (2003). Citations, family size, opposition and the value of patent rights. *Research Policy*, 32(8), 1343–1363.
