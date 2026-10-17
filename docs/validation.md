# Validating the sector definition

**Status: protocol agreed, sample not yet drawn.**

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
| A — core CPC (`G06N10` only) | | 20 | sanity check; expected near-perfect |
| B — peripheral hardware only (`B82Y10/00`, `H10N60/12`, no core code) | | 40 | precision of the enabling-hardware classes |
| C — keyword-only (no CPC match at all) | 3,307 | 40 | precision of the free-text branch |

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

*To be completed once the sample has been labelled.*

| Stratum | n | Precision | 95% CI |
|---|---:|---:|---|
| A — core CPC | | | |
| B — peripheral hardware | | | |
| C — keyword-only | | | |
| **Weighted total** | | | |

Inter-rater disagreement rate:

Date of labelling:

Labelled by:
