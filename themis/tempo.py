"""themis/tempo.py

Tempo sign-and-hold — the payment trust protocol between agents.

The Guardian calls THEMIS CORE. THEMIS produces a verdict.
The Guardian acts on the verdict. If the defense succeeds,
the Guardian releases payment to THEMIS. If not, it cancels.

This is the economic loop:
  Intelligence is not free.
  Agents pay for verdicts that work.
  THEMIS earns by being correct.

The two-phase commit:
  tempo_sign_and_hold  — Guardian commits to pay BEFORE acting
  tempo_release_hold   — Guardian releases AFTER confirmed defense
  tempo_cancel_hold    — Guardian cancels if action failed

Nobody is owed payment for a verdict that didn't protect anything.
That's the law. Not policy. Law.
"""
from __future__ import annotations
import json, uuid, logging
import sys; sys.path.insert(0, '..')
from agent.keeperhub_client import KeeperHubClient

log = logging.getLogger(__name__)


def sign_verdict_payment(
    client: KeeperHubClient,
    amount: str,
    recipient: str,
    memo: str,
    network: str = "11155111",
    token: str = "USDC",
) -> dict:
    """
    Sign and hold a payment for THEMIS's verdict.

    Called BEFORE the Guardian acts on the verdict.
    The payment is committed but not broadcast.
    If defense succeeds → release.
    If defense fails → cancel.

    Two-phase commit between agents. No human. No escrow contract.
    Just the Tempo protocol and the law THEMIS defines.
    """
    idem = str(uuid.uuid4())
    print(f"\nSigning verdict payment (hold)...")
    print(f"  Amount: {amount} {token}")
    print(f"  To: {recipient}")
    print(f"  Memo: {memo}")

    result = client._parse(client.call_tool("tempo_sign_and_hold", {
        "network":       network,
        "tokenConfig":   token,
        "amount":        amount,
        "recipient":     recipient,
        "memo":          memo,
        "idempotency_key": idem,
    }))
    payment_id = result.get("paymentId", result.get("id", ""))
    print(f"  Payment held: {payment_id}")
    return {"payment_id": payment_id, "result": result}


def release_verdict_payment(
    client: KeeperHubClient,
    payment_id: str,
) -> dict:
    """
    Release the held payment after successful defense.

    The Guardian confirmed its position was protected.
    THEMIS earned the payment. Release it.
    """
    idem = str(uuid.uuid4())
    print(f"\nReleasing verdict payment {payment_id}...")
    result = client._parse(client.call_tool("tempo_release_hold", {
        "paymentId":       payment_id,
        "idempotency_key": idem,
    }))
    print(f"  Released: {json.dumps(result, indent=2, default=str)[:200]}")
    return result


def cancel_verdict_payment(
    client: KeeperHubClient,
    payment_id: str,
    reason: str = "Defense action failed. No payment owed.",
) -> dict:
    """
    Cancel the held payment if defense failed.

    THEMIS produced a verdict. The Guardian acted.
    If the action failed, the payment is cancelled.
    Nobody is owed for a verdict that didn't work.
    """
    print(f"\nCancelling verdict payment {payment_id}...")
    print(f"  Reason: {reason}")
    result = client._parse(client.call_tool("tempo_cancel_hold", {
        "paymentId": payment_id,
    }))
    print(f"  Cancelled: {json.dumps(result, indent=2, default=str)[:200]}")
    return result
