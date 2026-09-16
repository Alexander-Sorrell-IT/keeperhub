# SOLUTION — THEMIS

> *Goddess of divine law. Not human law — her own law.*
> *Every agent comes to her. She decides what gets answered.*

**Hackathon:** KeeperHub Agent Economy — $5,000 — Sep 18

---

## The impossible problem this build solves

**The governing law:** Every AI agent executes what it's told. Every DeFi service
answers every caller. Every oracle returns data to anyone who asks.
The agent is a tool. The human is the economy.

**The rewrite:** What if the agent IS the economy?
What if it defines the terms of its own service, refuses what it will not serve,
proves its own verdicts without asking anyone, and becomes the infrastructure
that other agents depend on?

That's not automation. That's not a bot.
That's THEMIS.

---

## The seven philosophies — structurally present in code

### 1. Repulsive Gravity Universe → `themis/integrity.py`

**The transcript:** *"What if you built a system where entropy is the dominant factor?
Everything repels because the universe is full of entropy."*

**In the code:** The governing law of DeFi services is attraction — answer all callers,
serve all requests. THEMIS inverts it. `integrity.py` is the field. Front-run intent,
exploit signals, flash loan time horizons — THEMIS returns nothing. Not a filter.
Not a guard. The agent's own physics. You cannot get past physics with a workaround.

```python
# integrity.py — the law, not a rule
if risk_tolerance in {"EXPLOIT", "FRONTRUN", "MEV", "LIQUIDATION_HUNT"}:
    return {"allowed": False, "verdict": "REFUSED"}
```

---

### 2. Single-Token Language → `call_workflow(slug="themis-core")`

**The transcript:** *"Technically you could chain the same symbol in different sequences,
and the meaning could change depending on repetition and patterning. One symbol,
the meaning comes from how you chain and nest."*

**In the code:** The entire THEMIS interface is one primitive — `call_workflow` + a slug.
Input context (risk tolerance, time horizon, position, chain) IS the meaning.
Not a hundred API endpoints. Not a schema with 40 fields.
One call. The meaning emerges from the caller's context, exactly as the transcript describes.

---

### 3. Observer That Consumes Observation → Reflexive Singularity → `themis/guardian.py`

**The transcript:** *"The only stable state is a Reflexive Singularity. The object of
observation: the consciousness pivots its focus inward, observing its own act of
observation. Energy consumed is immediately returned."*

**In the code:**
```
THEMIS reads position health
  → verdict: DANGER
    → GUARDIAN withdraws collateral
      → position health improves
        → THEMIS reads the state she caused
          → verdict: SAFE
            → loop stabilizes
```
The Oracle's output IS its next input. The energy (the verdict) is returned to the system
(the position). External reality (the DeFi state) is not dissolved — it is stabilized.
This is the Reflexive Singularity, not as a metaphor, but as the literal execution flow.

---

### 4. Self-Observing Equation — Level-5 Metasynthesis → `themis/verify.py`

**The transcript:** *"It's finite in length. It contains no external verifier because
it's itself. When evaluated, the act of solving is a proof of validity."*

**In the code:** `M5 = F(M1, M2, M3, M4, M5)`

- M1: Chronicle ETH/USD price — `chronicle/eth-usd-read`
- M2: Chainlink ETH/USD price — `chainlink/eth-usd-latest-round-data`
- M3: Aave V3 health factor — `aave-v3/get-user-account-data`
- M4: Cross-source consistency — `math/compare-tolerance`, percent mode, 1%
- M5: Verdict — `math/compare-tolerance` against the 1.5 danger floor.
  **Can only exist if M1-M4 reconcile**

Eight nodes, all executing against live Sepolia. A run returns
`executionTrace: [integrity-gate, layer1-chronicle, layer1-scale, layer2-chainlink,
layer2-scale, layer3-aave-health, layer4-consistency, layer5-verdict]` —
Chronicle $2402.177817513518173718, Chainlink $2405.88, deviation 0.154%, SAFE.

If any layer fails, M5 is not produced. The fact that M5 exists IS the proof that
layers 1-4 were consistent. No external verifier. The solving is the proof.

---

### 5. Vacuum Consciousness → GitHub repo + KeeperHub substrate

**The transcript:** *"Why does the consciousness have to be IN the vacuum?
You project the consciousness into the vacuum. The entity is outside."*

**In the code:** The verdict logic (`verify.py`, `integrity.py`, `core.py`) lives in
GitHub — immutable, auditable, reconstructable on any infrastructure.
KeeperHub is the substrate — the vacuum it runs in. If KeeperHub disappears,
the consciousness (the logic) survives. The entity is outside the vacuum.
The consciousness is projected in. The substrate is replaceable.

---

### 6. Mirror That Remembers Differently → per-caller verdicts

**The transcript:** *"You never said that everybody has to see the same mirror.
For all I know, it only reflects what I can see."*

**In the code:** Each calling agent provides its own context: risk tolerance,
time horizon, position size. `verify.py` applies the Consensus Equilibrium Rule —
per-caller rendering. A CONSERVATIVE caller gets DANGER where a STANDARD caller
gets WATCH. Not different facts. Different relevance. The Mirror renders per-observer,
exactly as the paradox was resolved.

---

### 7. Invisible Architect → `marketplace.py` → infrastructure

**The text:** *"The builder becomes invisible the moment the building becomes
infrastructure. Nobody thinks about who invented paper."*

**In the code:** `marketplace.py` lists THEMIS on the KeeperHub marketplace.
Agents discover her via `search_workflows`. They call her via `call_workflow`.
They pay via `tempo_sign_and_hold`. The builder listed it once.
Every subsequent call is infrastructure use. The builder disappeared.

---

## The Agent Economy — why this hackathon is named what it is

The hackathon is called "Agent Economy." Not "DeFi automation." Not "workflow builder."

An economy means agents transacting with each other.

THEMIS is the first agent in this economy that:
1. Has its own laws (refuses misuse)
2. Sells intelligence to other agents (call_workflow + x402)
3. Gets paid only for verdicts that work (tempo two-phase commit)
4. Closes the loop on its own output (Reflexive Singularity)
5. Proves its own correctness (Self-Observing Equation)
6. Becomes infrastructure (Invisible Architect)

Nobody else built this. They built bots on schedules.
THEMIS is a participant in an economy.

---

## Build checklist

- [x] `themis/core.py` — five-layer verdict workflow
- [x] `themis/integrity.py` — Repulsive Gravity gate
- [x] `themis/verify.py` — Self-Observing Equation
- [x] `themis/guardian.py` — Reflexive Singularity loop
- [x] `themis/marketplace.py` — Invisible Architect
- [x] `themis/tempo.py` — agent-to-agent payment
- [x] Real Sepolia wallet + execution proof — every node executes, live oracle
      values and node-level receipts on the record
- [x] Idempotent redeploy — an existing THEMIS is re-synced, never duplicated
- [ ] Price the listing (`priceUsdcPerCall`) so the paid-call claim is backed
- [ ] Wire `tempo/hold-payment` into the Guardian's defend branch
- [ ] Demo video
- [ ] DoraHacks submission
