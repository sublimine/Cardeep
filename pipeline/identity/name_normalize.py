"""
pipeline/identity/name_normalize.py
Canonical dealer-name normaliser -- the SINGLE source of truth shared by the
deterministic clusterer (cluster_dealers.py) and the cross-source overlay
(cross_source_dedup.py).  Both modules previously carried a byte-identical
private copy of this function; consolidating it here removes the drift risk and
gives the country-pack lexicon (W1) one place to live.

WHY A TRANSLITERATOR INSTEAD OF ascii-fold (OPEN-C / gap C, project 360-A)
-------------------------------------------------------------------------
The legacy fold was ``NFKD -> str.encode('ascii', 'ignore')`` which *silently
deletes* every codepoint that has no ASCII decomposition.  For a Latin-script
name that only strips accents ('Peña' -> 'pena'); for a non-Latin-script name it
ERASES the whole identity:

    'Αθήνα'        -> ''      -> None   (dead name signal: no block-key emitted)
    'Αθήνα Motors' -> 'Motors'-> 'motors'  (worse: only the incidental Latin token
                                            survives, so every distinct Greek
                                            "... Motors" dealer over-merges)

That breaks the engine's genericity for non-Latin tenants (GR, BG, RU, GR, ...).
The fix transliterates non-Latin LETTERS to legible Latin ('Αθήνα' -> 'athina')
via ``anyascii`` (ISC-licensed, pure-Python, battle-tested) instead of dropping
them.

ES BYTE-IDENTITY (hard requirement)
-----------------------------------
Transliteration is applied PER CHARACTER and ONLY to letters the legacy fold
would have dropped.  Any character that the legacy ``NFKD + ascii-ignore`` fold
already turned into ASCII is kept EXACTLY as before, so Spanish / Latin input is
byte-identical to the previous behaviour:

    'ñ' -> 'n', 'á' -> 'a', 'ü' -> 'u', 'ç' -> 'c', 'ë'(Citroën) -> 'e',
    'Š'(Škoda) -> 's', Catalan 'L·L' -> 'll'  -- all unchanged.

Only non-Latin letters (which used to vanish) gain a value; symbols, marks and
digits the legacy fold dropped are still dropped (so e.g. '½', '®' do not start
injecting characters).  ``anyascii`` maps each codepoint independently, so the
per-character pass is identical to transliterating the whole string.
"""
from __future__ import annotations

import re
import unicodedata

from anyascii import anyascii

# ---------------------------------------------------------------------------
# Constants (moved verbatim from cluster_dealers.py / cross_source_dedup.py)
# ---------------------------------------------------------------------------

_RE_NON_ALNUM = re.compile(r"[^a-z0-9]")

# Societory suffixes to strip from normalised names (FIX B).
# Order matters: longer patterns must precede their shorter prefixes.
_LEGAL_SUFFIXES: tuple[str, ...] = (
    "sociedadlimitadaunipersonal",
    "sociedadanonima",
    "sociedadlimitada",
    "scoop",
    "scp",
    "slu",
    "sau",
    "sll",
    "sl",
    "sa",
)
# Pre-compile a single regex that matches exactly one suffix at the end.
_RE_LEGAL_SUFFIX = re.compile(
    r"(" + "|".join(re.escape(s) for s in _LEGAL_SUFFIXES) + r")$"
)

# Minimum characters required AFTER stripping the suffix; avoids turning
# short but valid names into empty strings (e.g. a hypothetical 2-char name).
_MIN_NAME_LEN_AFTER_STRIP = 3


def _ascii_fold_transliterate(name: str) -> str:
    """Fold ``name`` to ASCII, transliterating non-Latin letters instead of
    dropping them.

    Per character:
      * if the legacy ``NFKD + encode('ascii','ignore')`` fold yields ASCII,
        emit that byte-for-byte (so Latin / Spanish text is unchanged);
      * else, if the character is a LETTER (Unicode category ``L*``) that the
        legacy fold would have erased, transliterate it with ``anyascii``;
      * else (mark / symbol / digit / punctuation the legacy fold dropped),
        drop it -- preserving byte-identity for non-letter codepoints.
    """
    out: list[str] = []
    for ch in name:
        folded = unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode("ascii")
        if folded:
            out.append(folded)
        elif unicodedata.category(ch).startswith("L"):
            out.append(anyascii(ch))
        # else: a non-letter the legacy fold also dropped -> drop it.
    return "".join(out)


def normalize_name(name: str | None) -> str | None:
    """Transliterate -> lower -> strip non-[a-z0-9] -> strip legal suffix.

    The legal-suffix strip (FIX B) removes trailing societory forms such as
    'sa', 'sl', 'slu', 'sau', etc. so that 'AUTOMOCION DEL OESTE, S.A.' and
    'AUTOMOCION DEL OESTE' produce the same normalised key and are captured
    by edge 1 (exact name + muni) without needing fuzzy matching.

    A suffix is only removed when the remaining string has at least
    _MIN_NAME_LEN_AFTER_STRIP characters; otherwise the raw (no-suffix)
    form is returned unchanged to avoid false positives on very short names.

    Returns None if input is empty or produces an empty string.
    """
    if name is None or not isinstance(name, str) or not name.strip():
        return None
    clean = _RE_NON_ALNUM.sub("", _ascii_fold_transliterate(name).lower())
    if not clean:
        return None
    # Strip up to one legal suffix from the end (greedy: longest match wins
    # because _LEGAL_SUFFIXES is ordered longest-first and the regex
    # alternation is tried left-to-right).
    m = _RE_LEGAL_SUFFIX.search(clean)
    if m:
        stripped = clean[: m.start()]
        if len(stripped) >= _MIN_NAME_LEN_AFTER_STRIP:
            clean = stripped
    return clean
