# Validating the sector definition

**Status: the initial 100-family sample and validation results are available. Final-label decisions still need team confirmation, and communication-only families have not yet been sampled.**

The project brief asks us to hand-label about 100 random families, or to find
another defensible way of validating the query. This note sets out what we will
do and why, so that the result can be reported as a measurement rather than an
assertion.

## Why the work so far is not yet validation

We chose CPC codes by reading the official scheme definitions. That is
*construction*: it justifies why each code is in the list. It produces no
evidence about what the resulting set actually contains. Those are different
claims, and only the second is validation.

## Why we do not sample uniformly

A uniform draw of 100 families from the union of 50,239 would return roughly 93
families selected by CPC and 7 selected by keywords alone. The CPC branch is
dominated by `G06N10`, a class literally titled "Quantum computing" — its
precision is close to unity by construction, and confirming that across 93
families teaches us nothing we did not already know. Meanwhile the branch most
likely to be wrong would be represented by seven observations.

We therefore stratify, and sample from the parts of the definition that can
actually fail.

## Protocol

**Strata.** Three groups, sampled independently:

| Stratum | Population | Sample | What it tests |
|---|---:|---:|---|
| A — core CPC (`G06N10` only) | 6,293 | 20 | sanity check; expected near-perfect |
| B — peripheral hardware only (`H10N60/12`, no core code) | 563 | 20 | precision of the enabling-hardware class |
| C — keyword-only (no CPC match at all) | 3,468 | 60 | precision of the free-text branch |

Stratum C is weighted most heavily because it is where the uncertainty now sits.
After `B82Y10/00` was removed from the definition (`docs/methodology.md` §8),
keyword-only families rose from 6.6% to 14.8% of the dataset: roughly one family
in seven now rests on free-text matching with no classification support. The
branch that most needs measuring is also the one that grew.

Families reachable only through the quantum-communication codes
(`H04B10/70`, `H04L9/0852`) are a **scope** question rather than a precision
question — they are correctly classified, the issue is whether they belong in
this sector — and are handled in `docs/methodology.md`, not here.

**Labelling.** For each sampled family, read the title and the English abstract
of the earliest member and record one of:

- `1` — quantum computing: the invention concerns qubits, quantum processors,
  quantum algorithms, error correction, control electronics or software whose
  purpose is quantum computation;
- `0` — not quantum computing;
- `?` — cannot tell from title and abstract alone.

Each family is labelled independently by two team members. Disagreements are
resolved by discussion, and the disagreement rate is reported — it is a measure
of how well defined our own boundary is, and a high rate is itself a finding.

**Reporting.** Precision is computed per stratum, then recombined by population
weight:

$$
p = \frac{N_A p_A + N_B p_B + N_C p_C}{N_A + N_B + N_C}
$$

Report the per-stratum figures as well as the weighted total. A poor $p_C$ is
actionable: it means the keyword branch can be dropped, at a known cost of 6.6%
of the dataset.

## Recall

Precision measures what fraction of what we caught belongs. It says nothing about
what we missed. Recall cannot be measured without a gold-standard set we do not
have, so we approach it from the literature instead: compare our CPC list against
published quantum-patent studies and record, in `docs/methodology.md`, every code
they include that we do not, together with the reason for excluding it.

## Results

The currently committed final labels identify 36 relevant families out
of 100 sampled families: an unweighted sample precision of 36%.

The population-weighted estimate for groups A–C is 58.5%:

(6,293 × 70% + 563 × 5% + 1,796 × 35%) / 8,652 = 58.5%.

These percentages measure different things. The sample contains
20 families from A, 20 from B, and 60 from C. Weighting adjusts
their contributions to reflect each group's size in the database.

The 58.5% estimate covers groups A–C only: 8,652 of the 13,505
families in the filtered validation population. The remaining
4,853 communication-group families have not been sampled, so
full-sector precision has not yet been estimated.

These results remain subject to team confirmation of the final
decisions on disputed labels.

| Stratum | n | Precision | 95% CI |
|---|---:|---:|---|
| A — core CPC | 20 | 70.0% (14/20) | 48.1–85.5% |
| B — peripheral hardware | 20 | 5.0% (1/20) | 0.9–23.6% |
| C — keyword-only | 60 | 35.0% (21/60) | 24.2–47.6% |
| **Weighted estimate — A–C only** | 100 | **58.5%** | 43.7–73.3% |

Sector size at the time of labelling: 23,492 families (CPC 20,024, keywords
11,599, keyword-only 3,468).

Inter-rater disagreement rate: 23% (23 of 100 families; agreement 77%, Cohen's kappa 0.49)

Date of labelling:

Labelled by: Amirtay Almarua, Thekkedath Prince
