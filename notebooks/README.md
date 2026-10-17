# notebooks/

The analysis as actually run on the EPO Technology Intelligence Platform.

| Notebook | Covers | State |
|---|---|---|
| `STEP1_general_description.ipynb` | PW Step 1 — volume, growth, and the dating of the series | §1–§7 complete on PROD; §8 (technology mix) and §9 (geography) still to be written |

These notebooks run on TIP and nowhere else: they import `epo.tipdata.patstat`,
which is supplied by the platform, and they need authenticated access to PATSTAT.

## Working rules

Develop against `ENV = "TEST"`, the reduced ~10K-publication sample, and switch
to `ENV = "PROD"` for every number that will be reported. The code is identical;
only the constant changes.

**Watch for stale output.** Editing the environment constant without re-running
the cell leaves results on screen that were produced under the other setting,
with nothing to warn you. Re-run the configuration cell and check the printed
banner before trusting anything below it.

**Expensive queries are cached.** The first run of a section writes its result to
`outputs/`; later runs read from disk. A lost kernel then costs seconds rather
than a working session. Delete the cache file to force a recomputation.

## Structure of the Step 1 notebook

| § | Content |
|---|---|
| 1 | Setup and configuration |
| 2 | Applications and families; selecting the sector; branch counts |
| 3 | Three ways to date a patent |
| 4 | Methodological choices: truncation, PCT, fractional counting |
| 5 | Tables and attributes used |
| 6 | The counting machinery: scopes, counting functions, helpers |
| 7 | Volume, dating, and growth against all patenting |
| 8 | Technology mix — CPC subclasses and WIPO fields *(to be written)* |
| 9 | Geography — IP5 offices, applicant and inventor countries *(to be written)* |

Sections 8 and 9 are mostly calls to functions that §6 already defines —
`fractional_by_cpc_subclass`, `fractional_by_techn_field`, `count_by_office`,
`fractional_by_country`, and the presentation helpers. They should be written
against those, not from scratch, and each query wrapped in `cached()` the same
way §7 does.
