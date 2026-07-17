"""Market-intelligence compute layer (pilar 01-market-intelligence).

Jobs: compute_stats.py (M1/M3/M4/M5/M6/M7/M9/M10 -> market_stat), ingest_dgt.py
(DGT microdata -> dgt_transfer), corroborate.py (M8 -> dgt_corroboration).

cohort.py is the SHARED percentile/cohort helper (00-MASTER.md C-1/C-12): this pilar is
the first to build it, other pilares (03/04/06/07/09) import from here instead of
re-deriving their own median-by-cohort logic. Prohibited: a second independent
percentile/median implementation anywhere else in the codebase.
"""
from __future__ import annotations
