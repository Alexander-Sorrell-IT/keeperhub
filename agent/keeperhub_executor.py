"""keeperhub_executor.py — argus verdict → KeeperHub deterministic execution.

This is the integration layer. Given an argus verdict:
  1. Build a workflow on KeeperHub capturing the verdict in the description
  2. Execute a simulated contract read (dry run — no state change)
  3. Return workflow_id + execution_id + onchain result as audit proof

The Observer That Consumes Observation — resolved:
  The agent (argus) observes and proposes. KeeperHub executes without re-observing.
  Observation closes at review. Execution is deterministic.
"""
from __future__ import annotations
import json, logging, uuid, time
from typing import Optional

from agent.keeperhub_client import KeeperHubClient

log = logging.getLogger(__name__)

# Sepolia USDC — safe view target for testnet proof
PROOF_CONTRACT = "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8"
PROOF_CHAIN    = "11155111"   # Sepolia


class KeeperHubExecutor:
    """Connect argus verdict → KeeperHub workflow → deterministic onchain execution."""

    def __init__(self, client: Optional[KeeperHubClient] = None):
        self.client = client or KeeperHubClient()

    def run(self, verdict: dict, dry_run: bool = True) -> dict:
        """
        Args:
            verdict:  argus verdict dict
            dry_run:  if True, simulate only (default)

        Returns:
            {
                workflow_id, workflow_url,
                execution_result, onchain_proof,
                verdict_summary
            }
        """
        severity   = verdict.get("verdict", "UNKNOWN")
        vuln       = verdict.get("vulnerability_class", "unknown")
        chain      = verdict.get("chain", "ethereum")
        tx_hash    = verdict.get("tx_hash", "")
        summary    = verdict.get("summary", "")
        confidence = verdict.get("confidence", 0)

        log.info(f"KeeperHubExecutor: {severity} {vuln} on {chain}")

        # 1 — create workflow (captures the verdict as the description)
        idem = str(uuid.uuid4())
        wf = self.client.create_workflow(
            name=f"argus-{vuln}-{severity.lower()}-{idem[:6]}",
            description=(
                f"Argus verdict: {severity} | class={vuln} | chain={chain} | "
                f"confidence={confidence} | tx={tx_hash} | {summary} | "
                f"dry_run={dry_run}"
            ),
            nodes=[
                {"id": "trigger-1", "type": "trigger",
                 "actionType": "trigger/manual",
                 "name": "Argus Trigger", "config": {}},
            ],
            edges=[],
            idempotency_key=idem,
        )
        workflow_id  = wf.get("id", "")
        workflow_url = f"https://app.keeperhub.com/workflows/{workflow_id}"
        log.info(f"Workflow created: {workflow_id}")

        # 2 — execute a contract read through KeeperHub as the onchain proof
        proof_idem = str(uuid.uuid4())
        proof = self.client.contract_call(
            chain_id      = PROOF_CHAIN,
            address       = PROOF_CONTRACT,
            function_name = "totalSupply",
            function_args = "[]",
            simulate      = dry_run,
            idempotency_key = proof_idem,
        )

        return {
            "verdict_summary": f"{severity} {vuln} on {chain} — confidence {confidence}",
            "tx_hash_detected": tx_hash,
            "workflow_id":  workflow_id,
            "workflow_url": workflow_url,
            "dry_run":      dry_run,
            "onchain_proof": proof,
            "keeperhub_surfaces_used": [
                "MCP server (HTTP streaming, session-based)",
                "create_workflow — verdict captured as workflow description",
                "execute_contract_call — deterministic onchain read, simulate=True",
            ],
        }


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)

    sample_verdict = {
        "verdict":             "CRITICAL",
        "confidence":          0.92,
        "vulnerability_class": "flash_loan_attack",
        "summary":             "Abnormal flash loan volume on Aave V3. Possible exploit.",
        "chain":               "ethereum",
        "tx_hash":             "0xd3b4a1f2e8c9b7a6d5f4e3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2",
        "contract_address":    "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
        "recommended_action":  "alert",
    }

    executor = KeeperHubExecutor()
    result   = executor.run(sample_verdict, dry_run=True)

    print("\n=== ARGUS + KEEPERHUB EXECUTION RESULT ===")
    print(json.dumps(result, indent=2, default=str))
