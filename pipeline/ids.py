"""Time-ordered ULID-like identifier (48-bit ms time + 80-bit randomness)."""
from __future__ import annotations

import secrets
import time

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def ulid() -> str:
    ts = int(time.time() * 1000)
    rnd = int.from_bytes(secrets.token_bytes(10), "big")
    num = (ts << 80) | rnd
    out = []
    for _ in range(26):
        out.append(_CROCKFORD[num & 0x1F])
        num >>= 5
    return "".join(reversed(out))
