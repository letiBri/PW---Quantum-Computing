# Applicant Harmonization & Entity Linking

This document records the design choices, pipeline structure, and validation strategy for harmonizing applicant names (`applicants`).

---

## 1. The Problem: The "Name Game" in PATSTAT

In PATSTAT, the same corporate entity often appears under dozens of distinct spelling variants (*SIEMENS AG*, *Siemens Aktiengesellschaft*, *SIEMENS AKTIENGESELLSCHAFT MUENCHEN*, etc.). Treating each spelling variant as an independent entity fractures large players into smaller fragments and invalidates any concentration or market share metrics.

While PATSTAT's standardized name column (`psn_name`) provides an initial cleaning pass, critical issues remain unresolved:
* Variations caused by the presence or absence of legal forms (*Inc.*, *GmbH*, *AG*, *KK*, etc.).
* Dotted abbreviations and international formatting differences (*S.p.A.* vs *S P A*).
* Unmerged complex variants and international research institutions or subsidiaries.

---

## 2. Harmonization Strategies Evaluated

To resolve name variants, we evaluated and integrated three progressive levels of cleaning:

| Method | How it works | Strengths | Limitations |
|---|---|---|---|
| **A · Dictionary of Legal Forms** | Converts names to uppercase, strips punctuation, and trims legal-form keywords from the start and end of strings. | Excellent for variants differing only in standard formal suffixes. | Fails on dotted abbreviations, translations, or complex organizational structures. |
| **B · `cleanco` + Dictionary** | Integrates the `cleanco` Python package (specializing in global business entity extensions with or without dots) followed by Method A's keyword filter. | Corrects complex punctuation cleanly (e.g., transforms *FIAT S.p.A.* directly into *FIAT*). | Still requires dedicated rules for complex institutional or academic bodies. |
| **C · Terrorizer** | Advanced NLP and network theory techniques (name similarity scoring and community detection on name networks). | Highly effective at handling spelling variants, abbreviations, and entirely different name forms. | Requires manual oversight and validation of the generated clusters. |

---

## 3. Our Adopted Solution: Custom Pipeline (`my_harmonisation`)

Since automated dictionaries alone cannot flawlessly normalize complex research institutions (especially in Asian and academic contexts), we combined **Method B** with tailored custom rules.

Our final pipeline (`prepare_applicants`) performs the following operational steps:
1. **Pre-filtering:** Immediately drops rows with empty applicant names or `NaN` values to eliminate noise.
2. **Harmonization via `my_harmonisation`:** Applies `cleanco` and dictionary cleaning as a baseline, supplemented by targeted `if/else` rules to map specific complex variants (such as key research academies).
3. **Applicant Type Classification (`type`):** Refines PATSTAT sector strings into clean macro-categories (*firm*, *university*, *government / non-profit*, *hospital*, *individual*).
4. **Primary Country Assignment (`ctry`):** Assigns each applicant the country code that appears most frequently across its patent portfolio.
5. **Deduplication:** Consolidates data at the unique `(unit_id, applicant)` level for downstream concentration and trend analysis.

---

## 4. Validating the Method against a Gold Standard (not yet done)

To rigorously measure the performance and precision of our harmonization method, we test it against a **gold standard** dataset (`PATSTAT_500_label_datav4.csv`), containing applicant names manually grouped by domain experts.

### Evaluation Metrics 
We evaluate predicted groupings against the gold standard using **pairwise comparisons**:
* **Precision**: The share of merged name pairs that truly belong to the same organization (penalizes over-merging).
* **Recall**: The share of true organization pairs that our method successfully merged (penalizes under-merging).
* **F1-score**: The harmonic mean of precision and recall.
