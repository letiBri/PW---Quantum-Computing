# src/

The pipeline, as it is lifted out of the notebooks.

The project brief asks for a repository that reproduces the analysis end to end,
from the sector query to the Magic Quadrant, with configuration kept out of the
code. We are refactoring towards that shape as each step stabilises, rather than
writing modules for analysis we have not yet done.

## What is here

| File | Does | State |
|---|---|---|
| `config.py` | Reads `config/sector.yaml` and exposes it as a frozen object. Runs anywhere. | **Working** |
| `01_extract.py` | Builds the sector query and reports the contribution of each branch. Runs on TIP. | **Working** |

## What is planned

Following the structure set out in the project brief:

| File | Will do |
|---|---|
| `02_clean.py` | Family selection, applicant-name harmonisation, date handling; freezes the family-id set the later steps consume |
| `03_landscape.py` | Steps 1–2: volume, growth, technology mix, geography, concentration, entry |
| `04_present_score.py` | Step 3: influence, volume, success, globalization — the quadrant's vertical axis |
| `05_future_score.py` | Step 4: our own forward-looking algorithm |
| `06_quadrant.py` | Steps 3–5 figures, including the Magic Quadrant |

Until a step appears above as working, **the notebook is the source of truth for
it**, not a module in this folder. `notebooks/` holds the analysis as actually
run on TIP.

## One refactor worth doing early

`sector_family_ids()` returns a SQLAlchemy *query*, not a result. Every time it
is used to restrict a later query, PATSTAT re-derives the whole union — including
the text scan over titles and abstracts. For Step 1 this is tolerable; by Step 3,
with per-firm indicators, it will not be.

`02_clean.py` should execute the union **once**, persist the family ids, and hand
that frozen set to everything downstream. That is also what makes the pipeline
reproducible in the sense the brief asks for: a later step consumes a dataset,
not a query that might resolve differently on a different PATSTAT edition.
