"""keeperhub_executor.py — connects argus verdict → KeeperHub execution.

Flow:
  1. Receive argus verdict dict (from splunk_ai.py triage)
  2. Build workflow spec via workflow_builder.py
  3. Create workflow on KeeperHub
  4. Dry run — no chain touch, returns simulation result
  5. [Human approves] → execute → tx_hash + audit receipt

Usage:
    from agent.keeperhub_executor import KeeperHubExecutor

    executor = KeeperHubExecutor()
    result = executor.run(verdict, dry_run_only=True)   # review first
    result = executor.run(verdict, dry_run_only=False)  # execute for real
"""
from __future__ import annotations
import logging, json
from typing import Optional

from agent.keeperhub_client  import KeeperHubClient
from agent.workflow_builder  import build_workflow

log = logging.getLogger(__name__)


class KeeperHubExecutor:
    """Connects argus verdict to KeeperHub deterministic onchain execution."""

    def __init__(self, client: Optional[KeeperHubClient] = None):
        self.client = client or KeeperHubClient()

    def run(self, verdict: dict, dry_run_only: bool = True) -> dict:
        """
        Main entry point.

        Args:
            verdict:       argus verdict dict from splunk_ai.FoundationSec.triage()
            dry_run_only:  if True, simulate only — never touch the chain

        Returns:
            {
                "workflow_id": str,
                "dry_run":     dict,   # simulation result
                "execution":   dict,   # tx_hash + receipt (if not dry_run_only)
                "tx_hash":     str,    # convenience field
                "audit_url":   str,    # KeeperHub run URL
            }
        """
        severity = verdict.get("verdict", "UNKNOWN")
        log.info(f"KeeperHubExecutor.run: verdict={severity} dry_run_only={dry_run_only}")

        # 1. Build workflow spec from verdict
        spec = build_workflow(verdict)
        log.info(f"Workflow: {spec['name']}")

        # 2. Create workflow on KeeperHub
        workflow_id = self.client.create_workflow(
            name        = spec["name"],
            description = spec["description"],
            nodes       = spec["nodes"],
            edges       = spec["edges"],
        )
        log.info(f"Workflow created: {workflow_id}")

        # 3. Dry run — always, regardless of dry_run_only
        dry_result = self.client.dry_run(workflow_id, spec["inputs"])
        log.info(f"Dry run result: {json.dumps(dry_result, default=str)[:300]}")

        result = {
            "workflow_id": workflow_id,
            "workflow_name": spec["name"],
            "dry_run":     dry_result,
            "execution":   None,
            "tx_hash":     None,
            "audit_url":   f"https://app.keeperhub.com/workflows/{workflow_id}",
            "verdict":     verdict,
        }

        if dry_run_only:
            log.info("dry_run_only=True — stopping before execution")
            return result

        # 4. Execute — only if explicitly approved
        exec_result = self.client.execute(workflow_id, spec["inputs"])
        tx_hash = (
            exec_result.get("txHash") or
            exec_result.get("tx_hash") or
            exec_result.get("transactionHash", "")
        )
        run_id = exec_result.get("runId") or exec_result.get("id", "")

        log.info(f"Executed: tx_hash={tx_hash} run_id={run_id}")

        result["execution"] = exec_result
        result["tx_hash"]   = tx_hash
        if run_id:
            result["audit_url"] = f"https://app.keeperhub.com/runs/{run_id}"

        return result


# ── CLI smoke test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)

    # Sample argus verdict — replace with real one from triage
    sample_verdict = {
        "verdict":              "CRITICAL",
        "confidence":           0.92,
        "vulnerability_class":  "flash_loan_attack",
        "summary":              "Abnormal flash loan volume on Aave v3 — potential exploit.",
        "chain":                "ethereum",
        "tx_hash":              "0x0000000000000000000000000000000000000000000000000000000000000001",
        "contract_address":     "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
        "recommended_action":   "pause position",
        "poc_worthwhile":       True,
        "poc_block_number":     19234567,
    }

    executor = KeeperHubExecutor()
    result   = executor.run(sample_verdict, dry_run_only=True)

    print("\n=== DRY RUN RESULT ===")
    print(json.dumps(result, indent=2, default=str))
    print(f"\nWorkflow: {result['audit_url']}")
    print("Review the dry run above. To execute for real:")
    print("  executor.run(verdict, dry_run_only=False)")
