"""Step 0 — select the sector from PATSTAT.

Builds the query that defines the sector and reports how much each branch of the
definition contributes. This is the refactored form of what the Step 1 notebook
does in its section 2.1, with the codes and keywords read from
``config/sector.yaml`` rather than written into the code.

Runs only inside the EPO Technology Intelligence Platform, which supplies the
``epo.tipdata`` client and authenticated access to PATSTAT::

    python main.py

Expect a few minutes on PROD: the keyword branch scans titles and abstracts
across the whole database.
"""

from __future__ import annotations

from sqlalchemy import and_, distinct, func, not_, or_

from epo.tipdata.patstat import PatstatClient
from epo.tipdata.patstat.database.models import (
    TLS201_APPLN,
    TLS202_APPLN_TITLE,
    TLS203_APPLN_ABSTR,
    TLS224_APPLN_CPC,
)


# --------------------------------------------------------------------------- #
# Query building blocks
# --------------------------------------------------------------------------- #

def symbol_prefix_condition(symbol_column, codes):
    """OR-condition: the blank-stripped classification symbol starts with a code.

    PATSTAT pads CPC symbols to a fixed width (``F03B  13/14``), so blanks are
    removed on both sides before comparing. Matching is a string prefix, not a
    hierarchy walk — see docs/methodology.md, section 5.
    """
    symbol = func.replace(symbol_column, " ", "")
    return or_(*(symbol.like(code.replace(" ", "") + "%") for code in codes))


def keyword_condition(terms, exclusions=()):
    """Any term appears in the title or abstract, and no exclusion phrase does.

    Case-insensitive. A missing title or abstract is read as empty text: without
    the COALESCE, NOT applied to a NULL comparison is NULL, and SQL would drop the
    application silently instead of keeping it.
    """
    title = func.lower(func.coalesce(TLS202_APPLN_TITLE.appln_title, ""))
    abstract = func.lower(func.coalesce(TLS203_APPLN_ABSTR.appln_abstract, ""))
    match = or_(*(col.like(f"%{t.lower()}%") for t in terms for col in (title, abstract)))
    if not exclusions:
        return match
    excluded = or_(*(col.like(f"%{x.lower()}%") for x in exclusions for col in (title, abstract)))
    return and_(match, not_(excluded))


def families_by_cpc(db, prefixes):
    """Families with at least one application carrying one of the CPC prefixes."""
    return (
        db.query(TLS201_APPLN.docdb_family_id.label("docdb_family_id"))
        .join(TLS224_APPLN_CPC, TLS201_APPLN.appln_id == TLS224_APPLN_CPC.appln_id)
        .filter(symbol_prefix_condition(TLS224_APPLN_CPC.cpc_class_symbol, prefixes))
    )


def families_by_keywords(db, terms, exclusions=()):
    """Families with at least one application matching a keyword in title or abstract,
    that application carrying none of the exclusion phrases."""
    return (
        db.query(TLS201_APPLN.docdb_family_id.label("docdb_family_id"))
        .outerjoin(TLS202_APPLN_TITLE, TLS201_APPLN.appln_id == TLS202_APPLN_TITLE.appln_id)
        .outerjoin(TLS203_APPLN_ABSTR, TLS201_APPLN.appln_id == TLS203_APPLN_ABSTR.appln_id)
        .filter(keyword_condition(terms, exclusions))
    )


def sector_family_ids(db, cfg):
    """The sector: families matching the CPC codes OR the keywords.

    UNION removes duplicates, so a family caught by both branches counts once.
    """
    by_cpc = families_by_cpc(db, cfg.cpc_prefixes)
    if not cfg.keywords:
        return by_cpc.distinct()
    return by_cpc.union(families_by_keywords(db, cfg.keywords, cfg.keyword_exclusions))


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def count_families(patstat, db, query, label):
    """Execute a family-id query and report how many distinct families it returns."""
    sq = query.distinct().subquery()
    n = patstat.df(
        db.query(func.count(distinct(sq.c.docdb_family_id)).label("n"))
    ).loc[0, "n"]
    print(f"{label:<28} {n:>12,}")
    return int(n)
