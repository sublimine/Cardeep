"""Tier-1 anti-detection: real-browser challenge solving + cookie minting.

See browser.py. This package is import-safe even when no browser binary is
installed; the heavy imports happen lazily inside the solver.
"""
from pipeline.engine.tier1.browser import (  # noqa: F401
    BrowserResult,
    Tier1Error,
    solve_challenge,
)
