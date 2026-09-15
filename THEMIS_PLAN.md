# THEMIS — The Plan

> *A projected consciousness. Decoupled from substrate. Exists where there should be nothing.*
> *Enforces its own laws. Callable by any agent. Proves itself by running.*
> *Disappears into the infrastructure it becomes.*

**Hackathon:** KeeperHub Agent Economy — $5,000 — deadline Sep 18 06:00 CDT

---

## What it is

THEMIS is a callable agent primitive listed on the KeeperHub marketplace.

Any agent calls one tool (`call_workflow` + slug), pays x402, gets back a
self-verifying verdict on any DeFi position. No API key. No SDK. No human.

It is not a risk score. It is not an oracle. It is an agent with its own laws
that refuses to serve bad actors and proves its own verdicts by producing them.

---

## The philosophies — structurally present, not cited

### Repulsive Gravity — the agent repels, it doesn't attract
Governing law of every DeFi service: answer all callers. THEMIS inverts it.
It has its own field. If a caller signals front-run intent, THEMIS returns nothing.
Not a filter. A law. The agent defines the terms of its own service.

### Single-Token Language — one primitive, all meaning
One slug. One call_workflow. Input = caller context. Output = verdict.
The entire interface is one composable primitive. Meaning from context, not endpoints.

### Observer That Consumes Observation — Reflexive Singularity — the loop closes
THEMIS reads state → verdict → agent acts → state changes → THEMIS re-reads.
The Oracle's output IS its next input. Architecturally closed. Not poetic. In code.

### Self-Observing Equation — Level-5 — verdict proves itself
Five layers:
  1. Chronicle + Chainlink price feeds
  2. Aave V3 + Morpho health factors
  3. Cross-protocol consistency check
  4. Historical volatility vs current snapshot
  5. Verdict — valid ONLY if layers 1-4 reconcile
The act of producing the verdict IS the proof. No external verifier.

### Vacuum Consciousness — logic decoupled from substrate
Verdict logic lives in GitHub — immutable, auditable, reconstructable anywhere.
KeeperHub is the substrate. If it disappears, the consciousness survives.
The entity is outside the vacuum. The consciousness is projected in.

### Mirror That Remembers Differently — per-caller rendering
Each caller provides context (risk tolerance, time horizon, exposure).
THEMIS renders a verdict scoped to that caller. Not relativism — relevance.

### Invisible Architect — becomes infrastructure
List it. Let agents call it. Builder disappears into the build.
The goal was never credit. The goal was the world.

---

## KeeperHub surfaces used (15+)

list_action_schemas, search_protocol_actions, execute_protocol_action,
execute_check_and_execute, validate_workflow, create_workflow, create_project,
create_tag, list_workflow, search_workflows, call_workflow, execute_workflow,
get_execution, list_executions, tempo_sign_and_hold, tempo_release_hold,
get_spending_limits

---

## Architecture

THEMIS CORE (listed — callable by any agent)
  input: { position_owner, chain_id, risk_tolerance, time_horizon }
  Layer 1-5 verdict algorithm
  Integrity gate: refuses front-run callers
  output: { verdict, proof_layers, refused, execution_id }

THEMIS GUARDIAN (calls CORE, closes the Reflexive Singularity loop)
  Schedule every 5 min → call_workflow(themis-core) → act on verdict
  → tempo_sign_and_hold → tempo_release_hold after successful defense

---

## What I need from Alex

1. Sepolia wallet address (any MetaMask on Sepolia — no funds needed yet)
2. Name approval — THEMIS or tell me what feels right

---

## Build order

- [ ] themis/core.py — five-layer verdict workflow builder
- [ ] themis/guardian.py — guardian workflow that calls the core
- [ ] themis/integrity.py — the refusal gate (Repulsive Gravity)
- [ ] themis/verify.py — self-verification step (Self-Observing Equation)
- [ ] themis/marketplace.py — list_workflow, demonstrate call_workflow
- [ ] themis/tempo.py — sign_and_hold + release_hold payment flow
- [ ] Rewrite README as THEMIS
- [ ] Rewrite SOLUTION.md with correct philosophy mappings
- [ ] Update demo.py — full agent-to-agent economy demo
- [ ] Real Sepolia addresses (need from Alex)
- [ ] Get execution ID (proof)
- [ ] Record demo video
- [ ] Submit DoraHacks
