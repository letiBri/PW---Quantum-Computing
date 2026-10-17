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

The CPC subclass mix in Step 1 quantifies how much of the 50,239 families these
classes account for. That number decides the argument. Until then, every growth
and geography figure carries this caveat.

## 7. Open: the pre-2019 classification scheme

Quantum computing was classified under `G06N99/002` before `G06N10` was created.
CPC reclassification is in principle retroactive across the backfile, but
reclassification campaigns are never perfectly complete.

If pre-2019 families were not fully reclassified, our volume series will show a
spurious jump around the time `G06N10` came into use — an artefact of the
classification scheme rather than of the technology, and one that would lead
directly to a wrong statement about when the field took off.

**The diagnostic has not yet been run.** It is cheap: count families carrying
`G06N99/002` by priority year and compare against `G06N10` over the same years. If
the legacy code holds substantial mass in years where `G06N10` is thin, it belongs
in the definition for the historical period. The code list in `config/sector.yaml`
already carries it under `legacy`, unused.
