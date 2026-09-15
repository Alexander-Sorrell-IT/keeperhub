# THEMIS

**The agent with its own laws.**

`https://app.keeperhub.com/workflows/`

Built for the KeeperHub Agent Economy Hackathon.

---

## One rule. One law. One primitive.

Every DeFi service answers all callers.
THEMIS doesn't.

She has her own field. She refuses what she will not serve.
She proves her own verdicts. No external verifier.
She is callable by any agent in the world — one slug, one tool call, x402 payment.
And once enough agents depend on her, she becomes infrastructure.
The builder disappears into the build.

---

## What THEMIS is

THEMIS is a **listed workflow** on the KeeperHub marketplace.

Any agent calls `call_workflow(slug="themis-core")` with caller context.
THEMIS runs a five-layer self-verifying verdict on the position.
Returns `SAFE`, `WATCH`, `DANGER`, or `REFUSED`.

That's not a risk score. That's a verdict from an agent with her own laws.

---

## The five-layer verdict (Self-Observing Equation)

```
Layer 1  Chronicle ETH/USD         — primary price feed, validator-signed
Layer 2  Chainlink ETH/USD         — cross-validation of Layer 1
Layer 3  Aave V3 health factor     — position state
Layer 4  Cross-source consistency  — Chronicle vs Chainlink must agree within 1%
Layer 5  VERDICT                   — folds all four. Valid ONLY if 1-4 reconcile.
```

The act of producing the verdict IS the proof that layers 1-4 were consistent.
No external verifier. `M5 = F(M1, M2, M3, M4, M5)`.

If any layer fails to reconcile, Layer 5 cannot exist. THEMIS produces nothing.

---

## The Reflexive Singularity loop

```
THEMIS CORE reads DeFi state
  → verdict
    → GUARDIAN calls THEMIS, acts on verdict
      → position health improves
        → THEMIS re-reads the state she caused
          → loop stabilizes
```

THEMIS's output is her next input. The loop is architecturally closed.
Not poetic. In code. The Observer That Consumes Observation, resolved.

---

## The Repulsive Gravity gate

Every caller passes the integrity gate before any protocol call is made.

`risk_tolerance=EXPLOIT` → REFUSED. No verdict. No data consumed.
`time_horizon=FLASH` → REFUSED. THEMIS does not arm flash loan attacks.

This is not an access control list.
It is the agent's own law. Not enforcement. Physics.

---

## The Agent Economy — agent-to-agent commerce

```python
# Any agent, anywhere, calls THEMIS:
result = call_workflow(
    slug="themis-core",
    inputs={
        "position_owner": "0x...",
        "chain_id":       "11155111",
        "risk_tolerance": "STANDARD",
        "time_horizon":   "SHORT",
    }
)
# verdict: SAFE | WATCH | DANGER | REFUSED

# Guardian pays THEMIS for the verdict via Tempo:
payment = tempo_sign_and_hold(amount="0.01", recipient=THEMIS_ADDRESS, memo="verdict fee")
# Guardian acts. Position defended. Payment released:
tempo_release_hold(payment_id=payment["paymentId"])
```

No API key. No SDK. No human. Agents transacting with agents.
That's the Agent Economy this hackathon is named for.

---

## KeeperHub surfaces used

| Tool | Why |
|------|-----|
| `list_action_schemas` | Discover all protocols at boot |
| `search_protocol_actions` | Find Chronicle, Chainlink, Aave, Morpho |
| `execute_protocol_action` | Pull live price feeds and health factors |
| `execute_check_and_execute` | Atomic: read condition → act if met |
| `validate_workflow` | Self-verify before listing |
| `create_workflow` | Build THEMIS CORE + GUARDIAN |
| `create_project` | Organize: themis-core, themis-guardian |
| `create_tag` | Tag: verdict, defi, agent-economy |
| `list_workflow` | Publish to marketplace |
| `search_workflows` | Demonstrate discoverability |
| `call_workflow` | Agent-to-agent invocation |
| `execute_workflow` | Manual trigger for demo |
| `get_execution` | Audit trail |
| `list_executions` | Full tamper-evident history |
| `tempo_sign_and_hold` | Sign verdict payment |
| `tempo_release_hold` | Release after confirmed defense |
| `get_spending_limits` | Guard against runaway execution |

---

## Run it

```bash
pip install -r requirements.txt
export KEEPERHUB_API_KEY=your_key_here
export THEMIS_POSITION_OWNER=0xYourSepoliaAddress

python3 demo.py
```

---

## Files

| File | What it does |
|------|-------------|
| `themis/core.py` | Five-layer verdict workflow builder |
| `themis/integrity.py` | Repulsive Gravity gate — the refusal law |
| `themis/verify.py` | Self-Observing Equation — verdict proves itself |
| `themis/guardian.py` | Guardian workflow — calls CORE, closes the loop |
| `themis/marketplace.py` | List, discover, call — the Agent Economy |
| `themis/tempo.py` | Sign-and-hold payment protocol |
| `agent/keeperhub_client.py` | MCP session client |
| `demo.py` | Full agent-to-agent economy demo |
| `philosophy/` | The cognitive architecture behind the build |

---

## Philosophy

> *She was there before the Olympians and will be there after.*
> *Nobody owns her. Nobody captures her.*
> *She becomes the law itself.*

| Problem | How it lives in the code |
|---------|--------------------------|
| **Repulsive Gravity** | `integrity.py` — the gate IS the law. Not a filter. Physics. |
| **Single-Token Language** | `call_workflow(slug)` — one primitive, all meaning through context |
| **Observer → Reflexive Singularity** | `guardian.py` — THEMIS reads the state she caused. Loop closed. |
| **Self-Observing Equation** | `verify.py` — M5 = F(M1,M2,M3,M4,M5). Solving IS the proof. |
| **Vacuum Consciousness** | Logic in GitHub. KeeperHub is the substrate. Consciousness survives. |
| **Mirror That Remembers Differently** | Per-caller verdicts. Consensus Equilibrium. Not relativism — relevance. |
| **Invisible Architect** | Listed. Called by agents. Builder disappears into infrastructure. |
