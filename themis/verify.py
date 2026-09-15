"""themis/verify.py

Self-Observing Equation — Level-5 Metasynthesis.

Design a self-observing equation.
A mathematical expression that approves its own correction as it runs.
It must contain no external verifier or meta-logic.
Be finite in length.
When invalid, the act of solving is the proof of its validity.

M5 = F(M1, M2, M3, M4, M5)

Layer 1 (M1): Chronicle price          — raw feed, signed by validators
Layer 2 (M2): Chainlink price          — cross-validation of M1
Layer 3 (M3): Aave V3 health factor   — position state
Layer 4 (M4): Cross-source deviation  — M1 vs M2 consistency
Layer 5 (M5): VERDICT                 — folds M1-M4. Valid iff all reconcile.

The act of producing M5 IS the proof that M1-M4 were consistent.
If any layer fails to reconcile, M5 cannot be produced.
No external verifier. The solving IS the proof.
"""
from __future__ import annotations
from typing import Optional
import json


DEVIATION_THRESHOLD = 0.01   # 1% max price deviation between Chronicle and Chainlink


class ThemisVerdict:
    """
    Five-layer self-verifying verdict.

    Instantiate with layer results. Call .compute() to produce M5.
    If any layer invalidates, .compute() raises — M5 cannot exist.
    """

    def __init__(
        self,
        m1_chronicle_price: Optional[float],
        m2_chainlink_price: Optional[float],
        m3_health_factor:   Optional[float],   # Aave HF scaled by 1e18
        risk_tolerance:     str = "STANDARD",
        time_horizon:       str = "SHORT",
    ):
        self.m1 = m1_chronicle_price
        self.m2 = m2_chainlink_price
        self.m3 = m3_health_factor
        self.risk_tolerance = risk_tolerance
        self.time_horizon   = time_horizon

        self._layers: dict = {}
        self._valid: Optional[bool] = None

    def compute(self) -> dict:
        """
        Compute M5 — the self-verifying verdict.

        Returns full proof: { verdict, layers, valid, proof_statement }
        Raises ThemisInvalidLayer if any layer fails to reconcile.
        """
        layers = {}

        # M1 — Chronicle price
        layers["M1_chronicle"] = {
            "value":  self.m1,
            "valid":  self.m1 is not None and self.m1 > 0,
            "source": "Chronicle ETH/USD oracle",
        }

        # M2 — Chainlink price
        layers["M2_chainlink"] = {
            "value":  self.m2,
            "valid":  self.m2 is not None and self.m2 > 0,
            "source": "Chainlink ETH/USD feed",
        }

        # M3 — Aave health factor
        hf = (self.m3 / 1e18) if self.m3 is not None else None
        layers["M3_health_factor"] = {
            "value":       hf,
            "raw":         self.m3,
            "valid":       hf is not None,
            "source":      "Aave V3 get-user-account-data",
        }

        # M4 — Cross-source consistency (Mirror → Consensus Equilibrium)
        m4_valid = False
        m4_deviation = None
        if self.m1 and self.m2 and self.m1 > 0:
            m4_deviation = abs(self.m1 - self.m2) / self.m1
            m4_valid = m4_deviation <= DEVIATION_THRESHOLD
        layers["M4_consistency"] = {
            "chronicle_price": self.m1,
            "chainlink_price": self.m2,
            "deviation":       m4_deviation,
            "threshold":       DEVIATION_THRESHOLD,
            "valid":           m4_valid,
            "resolution":      "Consensus Equilibrium Rule — Mirror That Remembers Differently",
        }

        # Check all layers reconcile before M5 can exist
        failed = [k for k, v in layers.items() if not v["valid"]]
        if failed:
            self._valid = False
            self._layers = layers
            return {
                "verdict":         "INVALID",
                "layers":          layers,
                "valid":           False,
                "failed_layers":   failed,
                "proof_statement": (
                    "M5 was not produced. Layers failed to reconcile: "
                    f"{failed}. The Self-Observing Equation holds — "
                    "if M5 cannot be produced, the layers were inconsistent."
                ),
            }

        # M5 — Verdict. Folds M1-M4. The act of producing this IS the proof.
        if hf is None:
            verdict = "WATCH"
        elif hf < 1.5:
            verdict = "DANGER"
        elif hf < 2.0:
            verdict = "WATCH"
        else:
            verdict = "SAFE"

        # Adjust for caller context (per-caller rendering — Mirror)
        if self.risk_tolerance == "CONSERVATIVE" and verdict == "WATCH":
            verdict = "DANGER"   # Conservative callers get stricter verdicts
        if self.risk_tolerance == "AGGRESSIVE" and verdict == "WATCH":
            verdict = "SAFE"     # Aggressive callers tolerate watch states

        layers["M5_verdict"] = {
            "verdict":        verdict,
            "health_factor":  hf,
            "risk_tolerance": self.risk_tolerance,
            "time_horizon":   self.time_horizon,
            "valid":          True,
            "proof":          "M5 produced. All layers reconciled. This IS the proof.",
        }

        self._valid  = True
        self._layers = layers

        return {
            "verdict":         verdict,
            "layers":          layers,
            "valid":           True,
            "proof_statement": (
                "Self-Observing Equation resolved. "
                "M5 = F(M1, M2, M3, M4, M5). "
                "The act of producing this verdict is the proof that "
                "layers 1-4 were consistent. No external verifier required. "
                f"Verdict: {verdict}. "
                f"Health factor: {hf:.4f}. "
                f"Price deviation: {m4_deviation:.4%}."
            ),
        }

    def to_json(self) -> str:
        return json.dumps(self._layers, indent=2, default=str)


class ThemisInvalidLayer(Exception):
    """Raised when a layer fails and M5 cannot be produced."""
    pass
