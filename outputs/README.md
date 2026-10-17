# outputs/

Everything here is produced by the Step 1 notebook and regenerates if deleted.
All figures and tables below are from the run of 17 October, on PROD, with
`B82Y10/00` excluded from the definition.

## figures/

| File | Shows | Where it belongs |
|---|---|---|
| `fig_volume.png` | Families and applications per year, with the PCT share, at both levels | Landscape slide |
| `fig_dating.png` | The same patents dated by filing, publication and priority year | Technical appendix |
| `fig_growth.png` | Sector growth against all patenting, indexed to 2000 | Landscape slide |
| `fig_blocks.png` | Each block of the definition counted separately | **Technical appendix — see below** |

`fig_blocks.png` is the one to keep. It is the evidence behind excluding
`B82Y10/00`: the blue line is nanotechnology, peaking in 2004 and collapsing by
2014, and it was the whole of the sector's apparent decline. The orange line,
`G06N10`, is quantum computing, and it never declines. Note that the figure still
counts `B82Y10/00` — that is deliberate, since the point of the decomposition is
to show what the excluded code was doing.

A figure that shows how a definition was corrected says more about the quality of
the analysis than one more growth curve does.

## tables/

| File | Contents |
|---|---|
| `tab_growth.csv` | Counts and growth for the sector and for all patenting, at both levels, from 2000 and from 2010 |
| `tab_blocks.csv` | Families per year for each block of the definition |
| `sector_definition_counts.csv` | Families caught by the CPC branch, the keyword branch, their overlap, and the union |

## cache/

`volume.pkl`, `dating.pkl` and `blocks.pkl` are the aggregates behind the
figures. Each is a few kilobytes and each stands in for a PROD query of several
minutes, so they are committed: a teammate can re-run the analysis without
paying for the queries again.

They are derived data, not source. **If the sector definition changes, delete
them** — `cached()` will otherwise hand back results computed under the old
definition, with nothing to warn you. That is exactly what had to be done when
`B82Y10/00` was removed.
