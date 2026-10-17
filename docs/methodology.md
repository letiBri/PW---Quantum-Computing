# Methodological notes

Choices that shape every number in the analysis, recorded here so that each one
is argued once and can be cited from the deck's technical appendix.

---

## 1. Why the DOCDB family

A patent is valid only in the jurisdiction that grants it. An applicant who wants
protection in several countries files the same invention several times, and each
filing becomes a separate application in PATSTAT. The `docdb_family_id` links
them.

Counting applications therefore counts *filings*; counting families counts
*inventions*. The difference is not small. The largest family in our sector
contains **98 applications** for one invention with a 2002 priority — one count at
family level, 98 at application level.

We report both throughout. The ratio between them is not noise but a measurable
quantity: applications per family is a proxy for how widely applicants seek
protection, and in this sector it runs well above the global average (2.30 against
1.47 in 2022).

## 2. Which year

`tls201_appln` offers three dates, and the same invention falls in different years
depending on which is used:

| Column | What it is | Incomplete recent years |
|---|---|---|
| `appln_filing_year` | when this application was filed at its office | ~3 |
| `earliest_publn_year` | first publication of the application | ~1 |
| `earliest_filing_year` | earliest priority — first filing anywhere | ~3 |

We date families by the **minimum `earliest_filing_year`** across their members:
the first time the invention was filed anywhere in the world, which is the date
closest to the act of inventing. Applications are dated by their own filing year.

Publication-based dating would give a more up-to-date series — it is what EPO
statistics use — but it displaces inventions roughly 18 months from their origin,
which matters when the question is when a technology emerged.

## 3. Truncation, and why nothing is shaded

Applications publish about 18 months after priority and reach PATSTAT later
still, so the most recent priority years are structurally incomplete.

The course fixes the window at **2000–2022**. Rather than plotting incomplete
years and shading them grey, we close the series at the last year treated as
complete, so no incomplete year is ever drawn. In code this is
`LAST_COMPLETE_YEAR = YEAR_MAX`, which makes the shading helper a deliberate
no-op; it is kept and guarded so that widening the window restores the shading
without any other edit.

The hazard this avoids is specific and common: a raw PATSTAT series always falls
away in its final years, and reading that fall as a decline in the sector would be
simply wrong.

**One consequence to keep in mind.** Growth figures terminate on 2022. If that
year is not yet full in the PATSTAT edition TIP serves, every growth rate we
report is *understated*, and the honest wording is "at least" rather than a point
estimate. This should be checked against the dating figure in Step 1 before the
numbers go into the deck.

## 4. Fractional counting

When a unit belongs to several categories it is split equally among them: a family
in four CPC subclasses contributes ¼ to each, and a family with two Italian and
one German applicant contributes ⅔ to IT and ⅓ to DE. Each family therefore sums
to exactly 1, and every breakdown sums to the number of families.

Without this rule a breakdown by category sums to more than the number of units
and every share is overstated — in a sector where co-classification is routine,
substantially so.

## 5. Prefix matching is a string operation, not a hierarchy walk

CPC symbols are stored padded with blanks (`F03B  13/14`), so all matching is done
on the blank-stripped symbol. Matching is then by string prefix.

This has a consequence that is easy to get wrong. `G06N10/00` matches `G06N10/00`
and anything beginning with that exact string — it does **not** match `G06N10/20`,
because that string does not start with `G06N10/00`. Selecting a whole group means
writing the prefix at the level you want (`G06N10`), or listing every subgroup
explicitly. We list them explicitly in `config/sector.yaml`, so that each subgroup
can also be addressed on its own in the segment analysis.

## 6. Open: the scope boundary

The current definition includes two quantum-communication classes, `H04B10/70`
(photonic quantum communication) and `H04L9/0852` (quantum key distribution).

This makes the study one of quantum *technologies* rather than quantum
*computing*. The two have different filing dynamics and different geographies —
QKD in particular is heavily patented and geographically concentrated — so the
aggregate growth rate is a weighted average of two distinct phenomena, and the
applicant-country figures will reflect the mix.

The decision is defensible either way, but it has to be made explicitly:

- **Keep them** if the client's question is read as "quantum technology as an
  investment area", in which case the communication segment is part of the market
  and should be reported as its own segment, not silently merged.
- **Drop them** if the question is read as "quantum computing", which is how the
  sector is named in the brief and what Dell, as a computing-infrastructure
  company, would be buying.

The block decomposition in section 8 gives the first measurement. Quantum
communication is not marginal: 894 families with a 2022 priority year against
1,915 for `G06N10`, and it grows at 20.8% a year over the full window. It is
roughly a third of recent activity in our dataset, and it is a different market
with a different geography.

That size makes the silent-merge option untenable. Whichever way the boundary is
drawn, the communication codes have to be named and their contribution reported;
they cannot be folded into a single headline number without misleading the
reader. Until the team settles it, every growth and geography figure computed on
the union carries this caveat.

## 7. Resolved: there is no gap from the pre-2019 classification scheme

Quantum computing was classified under `G06N99/002` before `G06N10` was created.
CPC reclassification is in principle retroactive across the backfile, but
reclassification campaigns are never perfectly complete. Had ours been
incomplete, the volume series would show a spurious jump around the time
`G06N10` came into use, and we would have drawn a wrong conclusion about when
the field took off.

**We tested it, and there is no gap.** Counting families carrying `G06N99/002`
by priority year over 2000-2022 returns nothing: the legacy group is empty.
`G06N10`, meanwhile, is populated continuously across the same span, running at
15 to 55 families a year through the 2000s before it begins to climb.

Both facts point the same way. The backfile was reclassified, old quantum
computing families now carry `G06N10`, and the legacy group has been emptied
behind them. There is no correction to make and no historical blind spot.

This matters for how the takeoff can be described. Because the early years are
genuinely sparse rather than merely missing, the inflection around 2013-2015 and
the acceleration from 2018 are observations we can state rather than hedge.
`G06N99/002` stays recorded under `legacy` in `config/sector.yaml`, unused, with
this result as the reason.

## 8. Resolved: the volume curve measures two different things

The Step 1 volume series has an odd shape. At family level it rises from about
1,065 families in 2000 to roughly 1,750 in 2004, falls to about 380 by 2013-2014,
and only then climbs to 3,974 in 2022 — a fall of nearly 80% from peak to trough
across a decade in which quantum computing research, funding and publication
output all rose.

We did not believe that was a property of the technology, so we decomposed the
series: each block of the definition counted on its own, same window, same
counting rules. The result (`outputs/tables/tab_blocks.csv`) is unambiguous.

| Block | 2000 | 2010 | 2022 | CAGR 2000-2022 |
|---|---:|---:|---:|---:|
| `B82Y10/00` nanotechnology | 1,039 | 942 | 1,034 | **-0.0%** |
| `G06N10` quantum computing | 15 | 19 | 1,915 | **+24.7%** |
| `H04L9/0852` + `H04B10/70` quantum communication | 14 | 40 | 894 | +20.8% |
| `H10N60/12` Josephson devices | 11 | 11 | 116 | +11.3% |

Three things follow, and together they settle the question.

**The hump is entirely `B82Y10/00`.** It accounts for 96% of the year-2000 mass
of these blocks and falls 89% from its 2004 peak to its 2014 trough — the
early-2000s nanotechnology wave, tagged retroactively by a scheme introduced long
after the filings it covers. The apparent decline of "the sector" through the
2000s was the decay of that wave, not anything happening in quantum computing.

**`B82Y10/00` carries no growth signal at all.** Over the full window it is flat:
1,039 families in 2000, 1,034 in 2022, a compound rate of zero. It contributes
the entire distortion and none of the trend.

**Quantum computing never declined.** `G06N10` runs flat and small through the
2000s, turns up around 2013, and rises monotonically thereafter: 15 families in
2000 to 1,915 in 2022, a 128-fold increase at 24.7% a year. Against all patenting
(4.46% at family level) that is **5.5 times the rate** over the full window and
**7.5 times** over 2010-2022.

### What this does to the reported figures

Any growth rate computed on the union from a 2000 base compares a population that
was 96% nanotechnology against one that is mostly quantum computing. It is not an
understated growth rate; it is a ratio between two different things. The headline
figures in the README are therefore stated on `G06N10`, with the union reported
separately and its composition named.

### Recommended change to the definition, not yet applied

`B82Y10/00` should come out of the headline definition. It adds no trend, it
dominates and distorts the early base, and the client's question is about quantum
computing. Three options, in the order we would defend them:

1. **Drop it**, and report quantum computing on `G06N10` plus the keyword branch.
2. **Keep it, intersected with a keyword** — a nanotechnology family enters only
   if it also mentions qubits or quantum computation. This recovers the genuine
   quantum-hardware overlap, which is real after 2015, without the 2000s wave.
3. **Keep it as its own segment**, never merged into a headline number.

Option 2 is the better analysis and is what we would adopt. It is **not yet
applied**: `config/sector.yaml` still carries the definition that produced the
committed outputs, because changing the definition means re-running the pipeline
and every figure with it. Config and results should move together or not at all.
