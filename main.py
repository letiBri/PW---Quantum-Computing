"""Execute the main pipeline.

Combines all the scripts from 'src' folder and runs the main pipeline.  
"""

from src.stage00_config import load_config
from src.stage01_extract import count_families, families_by_cpc, families_by_keywords, sector_family_ids
from src.stage02_clean import family_scope, application_scope, Scope
from src.stage03_landscape import analyse_volume, analyse_technology_mix, analyse_geography

from epo.tipdata.patstat import PatstatClient
from pathlib import Path


def main():
    # load config 
    cfg = load_config()
    patstat = PatstatClient(env=cfg.env)
    db = patstat.orm()

    # load necessary variables
    SECTOR_NAME = cfg.sector_name

    # info
    print(f"{cfg.sector_name} | env: {cfg.env} | {cfg.year_min}-{cfg.year_max}")
    print("-" * 42)

    # count families obtained by cpc / keywords and their union
    n_cpc = count_families(patstat, db, families_by_cpc(db, cfg.cpc_prefixes), "CPC branch")
    n_kw = count_families(patstat, db, families_by_keywords(db, cfg.keywords, cfg.keyword_exclusions),
                          "Keyword branch")
    n_union = count_families(patstat, db, sector_family_ids(db, cfg), "UNION (the sector)")

    # The decomposition is what makes the two branches interpretable: how much
    # does free text add that the classification system misses, and how much of
    # the keyword branch is independently confirmed?
    keyword_only = n_union - n_cpc
    overlap = n_kw - keyword_only
    
    print("-" * 42)
    print(f"{'keyword-only families':<28} {keyword_only:>12,}  ({keyword_only / n_union:.1%} of sector)")
    print(f"{'confirmed by both':<28} {overlap:>12,}  ({overlap / n_kw:.1%} of keyword branch)")
    print("-" * 42)

    # get sector ids
    sector_ids = sector_family_ids(db, cfg)

    # calculate scopes (dataframes)
    SCOPES = [
        Scope("all patents", "family",      family_scope()),
        Scope(SECTOR_NAME,   "family",      family_scope(sector_ids)),
        Scope("all patents", "application", application_scope()),
        Scope(SECTOR_NAME,   "application", application_scope(sector_ids)),
    ]

    # analyse 
    analyse_volume(SCOPES, sector_ids)
    analyse_technology_mix(SCOPES)
    analyse_geography(SCOPES)
    


if __name__ == "__main__":
    main()