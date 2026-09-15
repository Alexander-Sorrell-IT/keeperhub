"""keeperhub_client.py — session-aware HTTP client for the KeeperHub MCP server.

KeeperHub MCP uses HTTP Streaming MCP (2025-06-18):
  1. POST /mcp  { method: "initialize" }  → get mcp-session-id header
  2. POST /mcp  { method: "notifications/initialized" }  with session header
  3. All subsequent calls include the mcp-session-id header

Auth: Bearer token via KEEPERHUB_API_KEY env var.
"""
from __future__ import annotations
import os, json, logging, requests
from typing import Optional

log = logging.getLogger(__name__)

KH_MCP_URL = os.getenv("KEEPERHUB_MCP_URL", "https://app.keeperhub.com/mcp")
KH_API_KEY = os.getenv("KEEPERHUB_API_KEY", "")


class KeeperHubClient:
    def __init__(self, api_key: str = KH_API_KEY, mcp_url: str = KH_MCP_URL):
        if not api_key:
            raise ValueError("KEEPERHUB_API_KEY not set")
        self.api_key  = api_key
        self.mcp_url  = mcp_url.rstrip("/")
        self._req_id  = 0
        self._session = None

    @property
    def _headers(self) -> dict:
        h = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
            "Accept":        "application/json, text/event-stream",
        }
        if self._session:
            h["mcp-session-id"] = self._session
        return h

    def _post(self, body: dict) -> dict:
        r = requests.post(self.mcp_url, headers=self._headers,
                          json=body, timeout=60)
        r.raise_for_status()
        sid = r.headers.get("mcp-session-id")
        if sid:
            self._session = sid
        if not r.content:
            return {}
        resp = r.json()
        if "error" in resp:
            raise RuntimeError(f"KeeperHub MCP error: {resp['error']}")
        return resp.get("result", {})

    def _ensure_init(self):
        if self._session:
            return
        self._req_id += 1
        self._post({"jsonrpc": "2.0", "id": self._req_id, "method": "initialize",
                    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                               "clientInfo": {"name": "argus-keeperhub", "version": "1.0"}}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        log.info(f"KeeperHub session established")

    def call_tool(self, name: str, arguments: Optional[dict] = None) -> dict:
        self._ensure_init()
        self._req_id += 1
        return self._post({"jsonrpc": "2.0", "id": self._req_id,
                           "method": "tools/call",
                           "params": {"name": name, "arguments": arguments or {}}})

    def list_tools(self) -> list[dict]:
        self._ensure_init()
        self._req_id += 1
        return self._post({"jsonrpc": "2.0", "id": self._req_id,
                           "method": "tools/list", "params": {}}).get("tools", [])

    # ── workflow ───────────────────────────────────────────────────────
    def create_workflow(self, name: str, description: str,
                        nodes: list, edges: list,
                        idempotency_key: str = "") -> dict:
        args = {"name": name, "description": description,
                "nodes": nodes, "edges": edges}
        if idempotency_key:
            args["idempotency_key"] = idempotency_key
        return self._parse(self.call_tool("create_workflow", args))

    def execute_workflow(self, workflow_id: str) -> dict:
        return self._parse(self.call_tool("execute_workflow",
                                          {"workflowId": workflow_id}))

    def get_execution(self, execution_id: str) -> dict:
        return self._parse(self.call_tool("get_execution",
                                          {"executionId": execution_id}))

    # ── direct execution ───────────────────────────────────────────────
    def contract_call(self, chain_id: str, address: str,
                      function_name: str, function_args: str = "[]",
                      simulate: bool = True,
                      idempotency_key: str = "") -> dict:
        """Read or simulate a contract call through KeeperHub."""
        args = {
            "contract_address": address,
            "chain_id":         chain_id,
            "function_name":    function_name,
            "function_args":    function_args,
            "simulate":         simulate,
        }
        if idempotency_key:
            args["idempotency_key"] = idempotency_key
        return self._parse(self.call_tool("execute_contract_call", args))

    def get_direct_status(self, execution_id: str) -> dict:
        return self._parse(self.call_tool("get_direct_execution_status",
                                          {"executionId": execution_id}))

    # ── helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _parse(result: dict) -> dict:
        for c in result.get("content", []):
            if c.get("type") == "text":
                try:    return json.loads(c["text"])
                except: return {"raw": c["text"]}
        return result
