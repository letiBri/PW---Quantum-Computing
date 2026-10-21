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
├── src/                     modules and scripts for the main pipeline
├── outputs/
│   ├── cache/               cached values to avoid longs cell execution
│   ├── figures/             figures referenced by the deck
│   └── tables/              result tables
├── docs/
│   ├── methodology.md       choices that need defending, and why we made them
│   └── validation.md        the Step 0 validation protocol and its results
├── tests/
├── main.py                  main pipeline, as it is refactored out of the notebooks
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
programming. To these we add one enabling-hardware class, `H10N60/12`
(Josephson-effect devices), and two quantum-communication classes, `H04B10/70`
and `H04L9/0852`.

One code was removed on evidence. `B82Y10/00` — *nanotechnology for information
processing, storage or transmission, e.g. quantum computing* — reads like an
obvious inclusion and was in our first definition. Counted on its own it turned
out to be measuring the early-2000s nanotechnology wave: 44% of the dataset, 96%
of the year-2000 families, and a compound growth rate of exactly zero across the
window. `docs/methodology.md` §8 sets out the evidence; `config/sector.yaml`
records the exclusion.

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
| CPC | 20,024 | 85.2% |
| Keywords | 11,599 | 49.4% |
| — also found by CPC | 8,131 | 34.6% |
| — **keyword-only** | 3,468 | 14.8% |
| **Union (the sector)** | **23,492** | 100% |

Two things follow. First, **70% of keyword hits are independently confirmed by a
classification code**, which is the signature of a keyword list that is not
over-reaching — a runaway list would produce a large branch mostly disjoint from
CPC. Second, **3,468 families are visible only in text**: roughly one in seven.
Those are the families a classification-only study would miss, and they are also
the part of the definition most in need of validation.

Removing `B82Y10/00` cut the dataset from 50,239 families to 23,492, a little
over half. That is the measure of how much of the original "sector" was a
different technology.

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

A first pass over the whole dataset produced a curve that did not make sense: the
sector appeared to peak around 2004, lose nearly 80% of its volume by 2014, and
only then recover. Quantum computing did not contract by four fifths over that
decade, so we counted each block of the definition separately. That changed both
the definition and the finding; `docs/methodology.md` §8 carries the argument.

**The apparent decline belonged to a different technology.** `B82Y10/00` held 96%
of our year-2000 families and fell 89% from its 2004 peak to its 2014 trough —
the early-2000s nanotechnology wave, tagged retroactively by a classification
scheme introduced long after the filings it covers. Across the full window that
block is flat: 1,039 families in 2000, 1,034 in 2022, compounding at zero. It
supplied the entire distortion and none of the trend. It is now excluded, which
cut the dataset from 50,239 families to 23,492.

**On the corrected definition, the sector never declined.**

| | 2000 | 2022 | Growth | CAGR 2000–2022 |
|---|---:|---:|---:|---:|
| Quantum computing (families) | 50 | 3,100 | ×62 | **20.6%** |
| All patenting (families) | 914,442 | 2,389,730 | ×2.6 | 4.46% |

The sector compounds at **20.6% a year against 4.46% for patenting as a whole —
4.6 times the rate** — and over 2010–2022 at 32.3% against 6.24%, **5.2 times**.
The series is small and flat through the 2000s, turns up around 2013 and rises
monotonically thereafter. Counted on `G06N10` alone the core runs from 15
families in 2000 to 1,915 in 2022, a 128-fold increase at 24.7% a year.

**The early years are real, not missing.** Quantum computing sat under
`G06N99/002` before `G06N10` existed, so sparse early counts could have been a
reclassification artefact rather than a fact about the field. Querying the legacy
group returns nothing at all: the backfile was reclassified and the old group
emptied behind it. The 2013–2015 inflection is therefore an observation, not a
hedge.

**Quantum communication is a third of the field as we have drawn it.**
`H04L9/0852` and `H04B10/70` together reach 894 families with a 2022 priority
against 1,915 for `G06N10`, growing at 20.8% a year. A different market with a
different geography, and too large to merge silently into a headline figure —
which is why the scope boundary is stated rather than assumed.

**Inventions are protected somewhat more widely than average.** Dividing
applications by families gives 1.89 jurisdictions per invention in 2022 against
1.47 for patents generally, about 29% more. This figure was 2.30 on the
pre-correction dataset, so the nanotechnology families were inflating it — a
useful reminder that composition reaches further than the volume curve. The
remaining 29% premium is the honest number, and it prefigures the Globalization
indicator used in Step 3.

## Status

| Step | Content | State |
|---|---|---|
| 0 | Sector definition, extraction, cleaning | Initial validation sample and results committed; final-label confirmation and communication validation pending |
| 1 | General description: volume, growth, technology mix, geography | Volume, growth, the block decomposition, technology mix and geography complete|
| 2 | Competitive landscape: concentration, entrants, subfields, PEST | Not started |
| 3 | Present score: influence, volume, success, globalization | Not started |
| 4 | Future score: our own algorithm | Not started |
| 5 | Magic Quadrant | Not started |
| 6 | Strategic analysis and recommendation | Not started |

Two items are known gaps rather than work merely not yet reached.

**Validation is partially complete.** The committed final labels identify
36 relevant families among 100 sampled families. The population-weighted
estimate is 58.5% for groups A–C only. These groups cover 8,652 of the
13,505 families in the filtered validation population.

The remaining 4,853 communication-group families have not been sampled.
Full-sector precision has therefore not yet been estimated. The team
must also confirm the final decisions on disputed labels.
See `docs/validation.md` for the calculation and limitations.

**The scope boundary needs settling.** Including `H04B10/70` and `H04L9/0852`
makes this a quantum *technologies* study rather than a quantum *computing* one.
We now know the size of the question: 894 families with a 2022 priority against
1,915 for `G06N10`, growing at 20.8% a year. That is roughly a third of recent
activity, too large to merge silently into a headline figure. Either keep it and
report it as its own segment, or cut it — both are defensible, and leaving it
unstated is not.

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
