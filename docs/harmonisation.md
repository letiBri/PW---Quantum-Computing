# Applicant Harmonization in Quantum Computing

This document outlines the strategy, method evolution, and validation framework implemented to harmonize applicant names (`applicants`) for the competitive landscape analysis (`Step 2`).

---

## 1. The Problem: The "Name Game" in PATSTAT

Within PATSTAT, the exact same corporate or research entity frequently appears under dozens of distinct spelling and formal variants (*SIEMENS AG*, *Siemens Aktiengesellschaft*, *SIEMENS AKTIENGESELLSCHAFT MUENCHEN*, etc.). Treating each variant as an independent entity artificially fractures major market players into a multitude of smaller fragments, distorting any market share or concentration metrics.

While PATSTAT's standardized name column (`psn_name`) provides a foundational normalization pass, structural challenges remain unaddressed:
* Presence or absence of diverse legal forms (*Inc.*, *GmbH*, *AG*, *KK*, etc.).
* Dotted abbreviations and heterogeneous international naming conventions.
* The need to consolidate language variants, institutional abbreviations, and subsidiaries under their parent organizations.

---

## 2. Harmonization Strategies Evaluated

The cleansing pipeline builds upon progressive methodologies, evaluated both independently and in combination:

| Method | Description | Strengths | Limitations |
|---|---|---|---|
| **A · Dictionary of Legal Forms** | Uppercasing, punctuation removal, and trimming of legal-form keywords from the start/end of strings. | Effective for variants differing solely through standard formal suffixes. | Fails on dotted abbreviations, translations, or complex corporate groups. |
| **B · `cleanco` + Dictionary** | Integration of the `cleanco` Python package (specializing in global business entity extensions) followed by Method A's keyword filter. | Cleanly resolves complex punctuation and dotted abbreviations (e.g., turning *FIAT S.p.A.* into *FIAT*). | Still requires dedicated rules for major public institutions or academic bodies. |
| **C · Terrorizer** | Advanced NLP and network theory techniques (name similarity scoring and community detection). | Highly powerful at clustering variants and radically different naming forms. | Requires rigorous manual oversight of generated clusters and presents installation/dependency constraints. |

---

## 3. The Adopted Solution: Tailored Sector Pipeline

To overcome the limitations, the adopted pipeline relies on a custom tuning layer (`my_harmonisation`) combining:
1. **Preliminary Normalization:** Uppercasing, accent removal, special character stripping, and whitespace regularization.
2. **Institutional Wrapper & Prefix Removal:** Stripping recurring boilerplate wrappers (e.g., *Board of Trustees of...*, *Regents of...*) that conceal the true patent owner.
3. **Abbreviation & Filler Dictionaries:** Standardizing common cross-lingual tokens (e.g., mapping *Univ*, *Université*, *Universität* to *UNIVERSITY*; stripping redundant prepositions and articles).
4. **Manual Aliases for Top Players:** Regular-expression-driven rules ensuring high-precision mapping for core global quantum computing stakeholders (e.g., IBM, Google, Microsoft, D-Wave, key Chinese and Japanese research academies).

---

## 4. Entity Type Classification and Geographic Assignment

Once names are harmonized, the pipeline determines each applicant's key metadata attributes:
* **Applicant Type (`type`):** Derived from PATSTAT's `psn_sector` field or directly inferred from the raw name via keywords and legal forms, categorizing subjects into *firm*, *university*, *government / non-profit*, *hospital*, or *individual*.
* **Primary Country (`ctry`):** Assigns each applicant the stable country code that occurs most frequently across its patent portfolio.

---

## 5. Validation Against a Gold Standard

To quantitatively measure the harmonization pipeline's performance before deploying it across the entire quantum computing dataset, the rules are tested against a **gold standard** benchmark (`PATSTAT_500_label_datav4.csv`), consisting of names manually grouped by domain experts.

### Evaluation Metrics
The alignment between algorithmic predictions and ground truth organizations relies on complementary metrics:
* **Pairwise Precision, Recall, and F1-score:** Measure the share of correctly linked name pairs (penalizing over-merging / *false positives*) versus the share of true organizational pairs successfully captured (*false negatives*).
* **Homogeneity, Completeness, and V-measure (`sklearn`):** Evaluate clustering structure quality by ensuring that each predicted group contains a single true organization (homogeneity) and that every real organization is fully encapsulated within a single cluster (completeness).

Iterative auditing against the gold standard ensures the optimal calibration of methods A, B, and custom rules, establishing a robust foundation for market concentration and leadership analysis in quantum computing.
