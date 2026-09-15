"""themis/integrity.py

The Repulsive Gravity gate.

The governing law of every DeFi service: answer all callers.
THEMIS inverts it. She has her own field.
She repels misuse. Not a filter. A law.

If you made a universe where gravity repels instead of attracts,
objects don't fall toward each other — they maintain distance by nature.
THEMIS maintains distance from bad actors by nature.
Not enforcement. Physics.
"""
from __future__ import annotations
from typing import Optional


# Known exploit patterns in caller context
_REFUSED_RISK_TOLERANCES = {"EXPLOIT", "FRONTRUN", "MEV", "LIQUIDATION_HUNT"}
_REFUSED_TIME_HORIZONS   = {"INSTANT", "FLASH"}   # flash loan / same-block intent


class IntegrityGate:
    """
    THEMIS integrity gate — the Repulsive Gravity law.

    Evaluates caller context before any protocol call is made.
    If the caller signals intent to exploit, front-run, or hunt liquidations,
    THEMIS refuses. No verdict produced. No data consumed.

    This is not an access control list. It is the agent's own law.
    The agent defines the terms of its own service.
    """

    def __init__(self, strict: bool = True):
        self.strict = strict
        self._refused_count = 0
        self._served_count  = 0

    def evaluate(
        self,
        risk_tolerance: str,
        time_horizon: str,
        caller_id: Optional[str] = None,
    ) -> dict:
        """
        Evaluate caller context.

        Returns:
          { allowed: bool, reason: str, verdict: str }

        If allowed=False, THEMIS produces VERDICT_REFUSED.
        The caller receives nothing. The loop does not proceed.
        """
        risk  = risk_tolerance.upper().strip()
        horiz = time_horizon.upper().strip()

        # Hard refusal — known exploit patterns
        if risk in _REFUSED_RISK_TOLERANCES:
            self._refused_count += 1
            return {
                "allowed": False,
                "reason": (
                    f"THEMIS does not serve risk_tolerance={risk_tolerance}. "
                    "Repulsive Gravity: the field repels misuse by nature, not by rule."
                ),
                "verdict": "REFUSED",
                "refused_count": self._refused_count,
            }

        if horiz in _REFUSED_TIME_HORIZONS:
            self._refused_count += 1
            return {
                "allowed": False,
                "reason": (
                    f"THEMIS does not serve time_horizon={time_horizon}. "
                    "Flash loan and same-block execution windows are not served. "
                    "THEMIS protects positions — she does not arm attacks."
                ),
                "verdict": "REFUSED",
                "refused_count": self._refused_count,
            }

        # Allowed
        self._served_count += 1
        return {
            "allowed": True,
            "reason": "Caller context passes integrity gate.",
            "verdict": None,
            "served_count": self._served_count,
        }

    def stats(self) -> dict:
        total = self._refused_count + self._served_count
        return {
            "total_calls":    total,
            "served":         self._served_count,
            "refused":        self._refused_count,
            "refusal_rate":   self._refused_count / total if total else 0.0,
        }


# Module-level singleton — THEMIS has one gate
_gate = IntegrityGate()

def check(risk_tolerance: str, time_horizon: str, caller_id: str = None) -> dict:
    return _gate.evaluate(risk_tolerance, time_horizon, caller_id)

def gate_stats() -> dict:
    return _gate.stats()
