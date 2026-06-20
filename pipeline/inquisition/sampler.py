"""P09-S2 - muestreador de PRECISION (acceptance sampling).

Implementa, como FUNCIONES PURAS (sin DB, sin red), los planes de muestreo de
docs/architecture/verification/V6-STATISTICAL-RIGOR.md:

  - plan_zero_defect : plan AQL c=0 (V6 Tabla 2.2)  n = ceil(ln a / ln(1-p0))
  - sprt_plan/_decision/_evaluate : SPRT de Wald (V6 §3) con parada temprana
  - wilson_interval : intervalo de Wilson para el defect-rate (V6 §5.1)
  - precision_estimate : P-hat con cota inferior por peor caso (anti-maquillaje)

Es el nucleo del beyond-SOTA de P09: convierte "confia en mi quorum de conteo"
en un fiscal estadistico que certifica la PRECISION de fila con un IC defendible
y un veredicto re-ejecutable (misma semilla -> mismo plan -> mismo dictamen).

stdlib only (math + statistics.NormalDist) -> reproduce exactamente las tablas
de V6 sin depender de scipy en el camino caliente.
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Iterable

# Veredictos del SPRT.
ACCEPT = "accept"
REJECT = "reject"
CONTINUE = "continue"


def _z(conf: float) -> float:
    """z de dos colas para confianza `conf` (0.95 -> 1.95996, 0.99 -> 2.57583)."""
    if not (0.0 < conf < 1.0):
        raise ValueError("conf must be in (0,1)")
    return NormalDist().inv_cdf(1.0 - (1.0 - conf) / 2.0)


def plan_zero_defect(N: int, p0: float, conf: float) -> dict:
    """Plan ciego de muestreo cero-defecto (c=0), V6 §2.2.

    Para afirmar, con confianza `conf`, que la tasa real de defectos esta por
    DEBAJO de p0, el plan binomial-exacto es n = ceil(ln(a)/ln(1-p0)) con
    a = 1-conf, aceptando solo si los n re-chequeos salen limpios. n se capa al
    tamano del lote N (no se puede muestrear mas que el lote).

    V6 Tabla 2.2 (p0=1%): n = 299 @95%, 459 @99%, 688 @99.9%.
    """
    if not (0.0 < p0 < 1.0):
        raise ValueError("p0 must be in (0,1)")
    if N <= 0:
        raise ValueError("N must be positive")
    alpha = 1.0 - conf
    n = math.ceil(math.log(alpha) / math.log(1.0 - p0))
    n = min(n, int(N))
    return {"n": n, "c": 0, "p0": p0, "conf": conf, "N": int(N)}


def wilson_interval(d: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    """Intervalo de Wilson para la proporcion de defectos d/n, V6 §5.1.

    Mejor que Wald cerca de 0 (donde Wald colapsa) y nunca se sale de [0,1].
    Para d=0 limpio con n=300 @95% la cota superior es ~1.26%.
    """
    if n <= 0:
        return (0.0, 1.0)
    if d < 0 or d > n:
        raise ValueError("require 0 <= d <= n")
    z = _z(conf)
    phat = d / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = phat + z2 / (2 * n)
    half = z * math.sqrt(phat * (1 - phat) / n + z2 / (4 * n * n))
    lo = (center - half) / denom
    hi = (center + half) / denom
    return (max(0.0, lo), min(1.0, hi))


def sprt_plan(p1: float, p2: float, alpha: float, beta: float) -> dict:
    """Lineas de decision del SPRT de Wald (V6 §3.1).

    H0: p = p1 (AQL, bueno)  vs  H1: p = p2 (LTPD, malo).
    Tras m items con d defectos:
        aceptar  H0  cuando  d <= s*m - h1
        rechazar (H1) cuando d >= s*m + h2
        si no, continuar.

    Reproduce V6 §3.2 (p1=.005, p2=.02, a=.05, b=.10):
        k=1.4014, s=0.010841, h1=2.0625, h2=1.6065.
    """
    if not (0.0 < p1 < p2 < 1.0):
        raise ValueError("require 0 < p1 < p2 < 1")
    if not (0.0 < alpha < 1.0 and 0.0 < beta < 1.0):
        raise ValueError("alpha, beta must be in (0,1)")
    A = (1.0 - beta) / alpha
    B = beta / (1.0 - alpha)
    k = math.log(p2 * (1 - p1) / (p1 * (1 - p2)))
    s = math.log((1 - p1) / (1 - p2)) / k
    h1 = math.log(A) / k
    h2 = -math.log(B) / k
    return {"p1": p1, "p2": p2, "alpha": alpha, "beta": beta,
            "A": A, "B": B, "k": k, "s": s, "h1": h1, "h2": h2}


def sprt_decision(m: int, d: int, plan: dict) -> str:
    """Un paso del SPRT: ACCEPT (<=AQL), REJECT (>=LTPD) o CONTINUE."""
    s, h1, h2 = plan["s"], plan["h1"], plan["h2"]
    if d >= s * m + h2:
        return REJECT
    if d <= s * m - h1:
        return ACCEPT
    return CONTINUE


def sprt_evaluate(scores: Iterable, plan: dict, n_max: int | None = None) -> dict:
    """Recorre una secuencia de defectos (1=defecto, 0=limpio) bajo el SPRT y
    para en el primer cruce de frontera (V6 §3).

    Truncado (V6 §3.3): si a `n_max` (por defecto 1.5x el n del plan fijo) sigue
    sin decidir, cae a la regla de punto medio (acepta si la tasa observada esta
    en/bajo el midpoint s, si no rechaza). Si la secuencia se agota sin decision
    ni truncado -> CONTINUE.

    Devuelve {verdict, m_stop, defects}.
    """
    d = 0
    m = 0
    for raw in scores:
        m += 1
        d += 1 if raw else 0
        verdict = sprt_decision(m, d, plan)
        if verdict != CONTINUE:
            return {"verdict": verdict, "m_stop": m, "defects": d}
        if n_max is not None and m >= n_max:
            final = ACCEPT if d <= plan["s"] * m else REJECT
            return {"verdict": final, "m_stop": m, "defects": d}
    return {"verdict": CONTINUE, "m_stop": m, "defects": d}


def precision_estimate(d: int, n: int, conf: float = 0.95) -> dict:
    """Estimador de precision con IC, V6 §5.

    P-hat = 1 - d/n. `precision_lower` usa la cota SUPERIOR del defect-rate
    (no la inferior): la precision que reportamos es la del PEOR caso defendible
    al nivel `conf` -- doctrina anti-maquillaje (cero por ausencia no infla).
    """
    if n <= 0:
        return {"precision": None, "defect_rate": None, "defect_ci": (0.0, 1.0),
                "precision_lower": None, "n": 0, "d": d}
    lo, hi = wilson_interval(d, n, conf)
    return {"precision": 1.0 - d / n, "defect_rate": d / n, "defect_ci": (lo, hi),
            "precision_lower": 1.0 - hi, "n": n, "d": d}
