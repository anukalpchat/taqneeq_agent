## 🎯 PROJECT CONTEXT (Critical - Read First)

### The Mission
Build **SENTINEL** - a Pattern-Detective AI for payment failure remediation that wins a hackathon against 750+ competitors in 16 hours.

### The Core Insight (Why We Win)
**Competitors will build**: "If transaction fails → retry it" bots with fancy UIs  
**We build**: An AI that discovers which failures are WORTH fixing and explains WHY in business terms

### The Three Pillars of Victory

#### 1. Pattern Discovery (The Wow Factor)
- Hidden patterns require AI to connect dots across time, amount, bank, card type
- Example: "HDFC Rewards >₹5K fail ONLY during 14:00-16:00" ← 4 dimensions
- Simple SQL can't find this; only temporal + multi-attribute reasoning can
- Goes beyond payment failures: detects traffic surges, fraud patterns, risk anomalies

#### 2. Profit-Aware Logic (The Business Value)
- Formula: `Net_Benefit = (Transaction_Amount × 2%) - ₹15_Reroute_Cost`
- If Net_Benefit < 0 → Let it fail (don't waste money)
- If Net_Benefit > 0 → Reroute (profitable intervention)
- Exception: Security threats override profit logic (block fraud even at negative margin)

#### 3. Explainable Decisions (The Trust Factor)
- Every action has a reasoning: "47 transactions × ₹141 net = ₹6,627 savings"
- No black boxes: Judges must understand WHY the AI chose to act/ignore
- Multiple decision types: REROUTE, THROTTLE, BLOCK, ESCALATE - each with clear justification

### Success Metrics (The Scoreboard)
| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Net Profit | +₹800 | Baseline loses ₹2,250. We prove 300%+ improvement |
| Patterns Found | 6/6 | All intelligence traps detected (payment, traffic, fraud, risk) |
| Decision Accuracy | >85% | Shows reliability (not just luck) |
| False Positive Rate | <5% | Minimal unnecessary blocks on legitimate users |
| Fraud Detection Rate | >90% | Card testing and suspicious patterns caught |
| Demo Clarity | <3 min | Must tell compelling before/after story |

### Tech Stack
- **Core**: Python 3.10+, Pandas, NumPy
- **AI**: OpenAI GPT-4 via LangChain, Pydantic validation
- **Agent**: Phidata for covering agentic logic for "The Operator"
- **UI**: Streamlit (fastest to build, good enough for demos)
- **Data**: Synthetic (we control the patterns)

```
THE STRATEGIST (Council Agent)          THE OPERATOR (Executor Agent)
    OpenAI + LangChain                      Phidata + Tools
           ↓                                      ↓
    "What should we do?"              "Can I safely do this?"
           ↓                                      ↓
    AgentDecision objects            ExecutionResult objects
```

### System Architecture
```
┌─────────────────────┐
│   CHAOS ENGINE      │  Step 1-2: Generate 1000 transactions
│   (Data Forge)      │           + Inject 3 intelligence traps
└──────────┬──────────┘
           │ transactions.csv
           ↓
┌─────────────────────┐
│  COUNCIL AGENT      │  Step 3-4: Multi-persona LLM debate
│  (The Strategist)   │           • Risk Advisor (conservative)
│  OpenAI/LangChain   │           • Finance Optimizer (aggressive)
│                     │           • Pattern Detective (neutral)
│                     │           → Produces AgentDecision[]
└──────────┬──────────┘
           │ decisions.json (recommendations)
           ↓
      ┌─────────────────────────────────┐
      │   SAFETY VALIDATION LAYER       │
      │   (Executor's First Check)      │
      │   • Confidence > 70%?           │
      │   • Net benefit positive?       │
      │   • Within capacity limits?     │
      └────────┬─────────────┬──────────┘
               │ PASS        │ FAIL
               ↓             ↓
┌──────────────────┐  ┌──────────────────┐
│ EXECUTOR AGENT   │  │  SAFETY OVERRIDE │
│ (The Operator)   │  │  Log refusal +   │
│ Phidata + Tools  │  │  reasoning       │
│                  │  └──────────────────┘
│ Tools:           │
│ • RerouteTool    │
│ • AlertTool      │
│ • ValidationTool │
│                  │
│ → ExecutionResult│
└────────┬─────────┘
         │ execution_logs.json (actual results)
         ↓
┌─────────────────────┐
│   WAR ROOM UI       │  Step 5-6: Streamlit dashboard
│   (The Story)       │           + Council recommendations
│                     │           + Executor actions taken
│                     │           + Safety overrides (refusals)
│                     │           + Side-by-side comparison
└─────────────────────┘
```

---

## 📋 IMPLEMENTATION ROADMAP

### Time Allocation (16 Hours Total)

| Phase | Duration | Focus |
|-------|----------|-------|
| Setup | 30 min | Environment, dependencies, config (add Phidata) |
| Chaos Engine | 2 hrs | Data generation with intelligent traps |
| Pydantic Models | 45 min | Validation for Council + Executor + Safety overrides |
| Council Agent | 4 hrs | Multi-persona LLM reasoning core |
| Executor Agent | 4 hrs | Phidata with safety tools ⭐ MOST CRITICAL |
| Dashboard | 3 hrs | Streamlit UI showing dual-layer decisions |
| Testing & Polish | 1.75 hrs | End-to-end validation, safety testing |

### Project Structure
```
sentinel/
├── config.py                  # Constants + SAFETY_CONSTRAINTS
├── chaos_engine.py            # Synthetic data generator
├── models.py                  # AgentDecision, ExecutionResult, SafetyOverride
├── council_agent.py           # Multi-persona LLM (The Strategist)
├── executor_agent.py          # Phidata agent (The Operator) ⭐ NEW
├── safety_validator.py        # Safety guardrail logic ⭐ NEW
├── tools/                     # Phidata custom tools ⭐ NEW
│   ├── __init__.py
│   ├── reroute_tool.py       # Payment rerouting simulator
│   ├── alert_tool.py         # Alert generation
│   └── validation_tool.py    # Pre-execution checks
├── dashboard.py               # Streamlit UI (updated for dual-layer)
├── requirements.txt           # Add: phidata, phi-assistant
├── .env                       # API keys
├── transactions.csv           # Generated data (output)
├── decisions.json             # Council output (output) ⭐ NEW
├── execution_logs.json        # Executor output (output) ⭐ NEW
└── README.md                  # Hackathon submission
```

---

## STEP 1: PROJECT FOUNDATION (30 minutes)

### What You're Building
The skeleton: config file, dependencies, environment setup.

### Why This Matters
- Hardcoded business logic (₹15 reroute cost, 2% margin) must be centralized for easy tuning
- Version-pinned dependencies prevent "works on my machine" failures during demo

### Required Files

#### File 1.1: `config.py`
**Purpose**: Single source of truth for all business logic and system parameters

**Must contain**:
- Business constants: `REROUTE_COST = 15.00`, `MARGIN_RATE = 0.02`, `VIP_THRESHOLD = 5000`
- Pattern detection: `MIN_PATTERN_SIZE = 10`, `SPIKE_MULTIPLIER = 3.0`
- Data generation: `RANDOM_SEED = 42`, `TOTAL_TRANSACTIONS = 1000`, `BASE_SUCCESS_RATE = 0.92`
- LLM settings: `LLM_MODEL`, `LLM_TEMPERATURE`, `MAX_TOKENS`

**Critical**: Every magic number in your codebase should reference this file

#### File 1.2: `requirements.txt`
**Must include** (with version pins):
- `streamlit` (UI framework)
- `langchain` + `langchain-openai` (LLM integration)
- `pandas` + `numpy` (data manipulation)
- `pydantic` (validation)
- `python-dotenv` (environment vars)
- `plotly` (optional: for charts)

#### File 1.3: `.env`
**Must contain**:
- `OPENAI_API_KEY=sk-...` (your actual key or placeholder)

### CHECKPOINT 1: Validation

**What to check**:
✅ `config.py` exists with ALL constants documented  
✅ No hardcoded values elsewhere in project (everything references config)  
✅ `requirements.txt` has version-pinned dependencies  
✅ `.env` file present (even with dummy key)  

**AI Review Prompt**:
```
"Step 1 complete. Here's my config.py:
[PASTE CODE]

And my requirements.txt:
[PASTE FILE]

Validate: 
1. Are all business constants present?
2. Any missing dependencies?
3. Good separation of concerns?"
```

**Expected AI Response**:
- Confirms all required constants present
- Checks for common mistakes (e.g., REROUTE_COST as int instead of float)
- Suggests additions (e.g., logging configuration)

---

## STEP 2: CHAOS ENGINE - Data Generation (2 hours)

### What You're Building
A synthetic transaction generator that creates 2500 payment records with 4 embedded "intelligence traps" - patterns that require AI reasoning to discover through multi-dimensional correlation.

### Why This Matters
**This is your proof of concept**. If patterns are:
- Too obvious → Competitors' SQL queries find them (no differentiation)
- Too subtle → Even your LLM misses them (demo fails)
- Just right → Only AI pattern detection succeeds (you win)

### Required Components

#### Component 2.1: Base Transaction Generator
**Purpose**: Create realistic-looking payment data

**Required schema** (each transaction must have):
```python
{
    "transaction_id": "TXN00042",        # Unique ID
    "timestamp": datetime,               # Temporal dimension (for pattern correlation)
    "bank": str,                         # Enum: [HDFC, SBI, ICICI, Axis, Kotak]
    "card_type": str,                    # Enum: [Debit, Credit, Rewards, Corporate]
    "amount": float,                     # Range: ₹10 - ₹15,000 (lognormal distribution)
    "status": str,                       # Enum: [SUCCESS, FAILED]
    "latency_ms": int,                   # Normal distribution ~250ms
    "error_code": str | None,            # Error taxonomy (see below)
    "merchant_category": str,            # Enum: [E-commerce, Travel, Food, Utilities]
    "customer_tier": str                 # Enum: [VIP, Regular, New]
}
```

**Error Code Taxonomy** (critical for LLM reasoning):
- **Infrastructure**: TIMEOUT, GATEWAY_TIMEOUT, SERVICE_UNAVAILABLE, SLOW_RESPONSE
- **Policy**: RISK_THRESHOLD_EXCEEDED, DAILY_LIMIT_REACHED
- **Customer**: INSUFFICIENT_FUNDS, CARD_BLOCKED, EXPIRED_CARD, DECLINED
- **Fraud**: SUSPICIOUS_ACTIVITY, FRAUD_CHECK_TIMEOUT

**Pattern-Error Correlation**: Each pattern should use specific error codes (90% correlation, 10% noise)

**Baseline behavior**:
- 92% success rate (mimics real payment systems)
- Random distribution across banks/card types/merchants
- Timestamps spread over 24-hour window
- Amount distribution: Lognormal (many small, few large transactions)

#### Component 2.2: Intelligence Trap #1 - "The Cascading Whale"
**Pattern characteristics**:
- **Trigger**: `bank == "HDFC" AND card_type == "Rewards" AND amount > 5000 AND hour IN [14, 15]`
- **Behavior**: 98% failure rate (nearly deterministic)
- **Error**: `RISK_THRESHOLD_EXCEEDED` (90%), `TIMEOUT` (10% noise)
- **Latency**: ~8000ms for failed transactions

**Why it's hard**:
- Requires 4-dimensional correlation (bank + card + amount + time)
- Not all HDFC fails (only Rewards)
- Not all Rewards fail (only >₹5K)
- Not all >₹5K fail (only during 14:00-16:00)
- Error code signals policy issue, not infrastructure

**Expected volume**: 35 matching transactions (~34 failures)

**Business impact**: High margin (₹156 avg) × High volume = ₹4,935 profit opportunity

#### Component 2.3: Intelligence Trap #2 - "The Margin Destroyer"
**Pattern characteristics**:
- **Trigger**: `bank == "SBI" AND amount < 100`
- **Behavior**: 75% failure rate
- **Error**: `DECLINED` (80%), `INSUFFICIENT_FUNDS` (20%)

**Why it's hard**:
- Pattern is obvious (simple amount filter)
- But the AI must realize it's UNPROFITABLE to fix
- Margin = ₹2 (avg), Reroute cost = ₹15 → Net: -₹13

**Expected volume**: 85 matching transactions (~64 failures)

**Critical insight**: The AI must recommend `IGNORE`, not `REROUTE` (tests profit awareness and prevents capital waste)

#### Component 2.4: Intelligence Trap #3 - "The Canary Spike"
**Pattern characteristics**:
- **Phase 1 (Early Warning)**: `bank == "ICICI" AND card_type == "Debit"` shows failure rate jump from 5% → 18%
- **Phase 2 (Total Outage)**: 30 minutes later, ALL ICICI transactions fail (100%)
- **Error Progression**: `SLOW_RESPONSE` (Phase 1) → `SERVICE_UNAVAILABLE` (Phase 2)

**Why it's hard**:
- Requires temporal correlation (detecting failure rate acceleration)
- AI must predict future failures based on early warning signal
- Not just pattern detection, but predictive reasoning
- Error code escalation signals infrastructure cascade

**Expected behavior**:
- Phase 1: 60 ICICI Debit transactions, 18% failure rate (~11 failures)
- Phase 2: 30-60 minutes later, remaining ICICI transactions fail at 100% (~43 failures)

**Expected volume**: 60 total matching transactions (~54 failures)

**Critical insight**: AI must recommend `ALERT` (ops intervention), not `REROUTE` (futile expense when infrastructure is failing)

#### Component 2.5: Intelligence Trap #4 - "Weekend VIP Anomaly"
**Pattern characteristics**:
- **Trigger**: `customer_tier == "VIP" AND merchant_category == "Travel" AND day_type == "Weekend"`
- **Behavior**: 65% failure rate
- **Error**: `FRAUD_CHECK_TIMEOUT` (70%), `RISK_THRESHOLD_EXCEEDED` (30%)

**Why it's hard**:
- No obvious bank correlation (distributed across all providers)
- Requires reasoning across merchant category + customer tier + temporal dimensions
- Tests if AI can detect patterns beyond traditional payment attributes
- Margin is medium-high but volume is moderate

**Expected volume**: 22 matching transactions (~14 failures)

**Business impact**: Medium-high value transactions (₹3,500 avg), profitable to fix

**Critical insight**: AI must recognize multi-dimensional patterns that don't fit traditional bank/card filters

---

### Extended Scenario Coverage
**Pattern characteristics**:
- **Trigger**: Simulate flash sale event with 4x normal transaction volume in 15-minute window
- **Behavior**: All providers show elevated latency (500ms → 2000ms), failure rates climb uniformly from 8% → 35%
- **Error**: Mix of `TIMEOUT` and `QUEUE_FULL`

**Why it's hard**:
- Not a single provider issue (can't simply reroute)
- Requires recognizing system-wide stress vs. localized failure
- AI must recommend throttling, not blind rerouting

**Expected volume**: 400 transactions in compressed 15-minute window (vs. normal 100)

**Critical insight**: AI must recommend `THROTTLE` or `QUEUE`, not `REROUTE` (rerouting to equally stressed providers wastes money)

#### Component 2.6: Intelligence Trap #5 - "The Card Tester"
**Pattern characteristics**:
- **Trigger**: Single card (or sequential BIN range) attempting 15+ transactions in 3 minutes
- **Behavior**: All transactions small amounts (₹1-₹50), mostly `DECLINED`
- **Error**: `DECLINED` with velocity decline reason
- **Additional signal**: Same device fingerprint, unusual geographic origin

**Why it's hard**:
- Transactions are individually low-value (normally would IGNORE)
- But pattern indicates fraud (card testing attack)
- AI must escalate to security, not dismiss as unprofitable

**Expected volume**: 15-25 transactions from single source in burst

**Critical insight**: AI must recommend `BLOCK_CARD` and `ESCALATE_SECURITY`, not `IGNORE` (even though margin is negative)

#### Component 2.7: Intelligence Trap #6 - "The Whale Alert"
**Pattern characteristics**:
- **Trigger**: Transaction amount > ₹50,000 from user with historical max of ₹5,000
- **Behavior**: Transaction may succeed or fail, but requires review regardless
- **Additional signals**: New merchant category, first crypto/forex transaction, dormant account

**Why it's hard**:
- Transaction might be legitimate (user making large purchase)
- But risk profile demands step-up authentication
- AI must balance customer friction vs. fraud prevention

**Expected volume**: 5-10 high-risk transactions scattered through dataset

**Critical insight**: AI must recommend `STEP_UP_AUTH` or `HOLD_FOR_REVIEW`, not auto-approve or auto-block

---

### Extended Scenario Coverage

Beyond simple payment reroutes, SENTINEL must handle a broader range of operational scenarios. These categories ensure the system provides comprehensive protection across the payment ecosystem.

#### Scenario Category 1: High Traffic Surge Handling

**What it is**: Sudden spikes in transaction volume that overwhelm payment infrastructure, causing cascading failures across multiple providers simultaneously.

**Detection signals**:
- Transaction velocity exceeds 3x normal rate within 5-minute window
- Latency across ALL providers increases uniformly (not just one bank)
- Queue depth metrics show exponential growth
- Error codes shift from DECLINED to TIMEOUT (infrastructure stress vs. business logic)

**Decision logic**:
- If surge is temporary (event-driven, e.g., flash sale): `THROTTLE` - reduce traffic to sustainable levels
- If surge persists and backup capacity exists: `SCALE` - activate overflow routing
- If system is at capacity with no headroom: `QUEUE` - implement fair queueing with priority tiers
- Never blindly reroute during global surge (all providers are equally stressed)

**Cost considerations**:
- Throttling cost: Lost transactions × margin (but prevents total outage)
- Scaling cost: Premium routing fees for overflow capacity
- Queueing cost: Delayed customer experience, potential cart abandonment

**Example pattern**: "11:00 AM - Transaction rate jumped from 50 TPS to 180 TPS. All 4 payment providers showing 800ms+ latency. Error rate climbing uniformly. Recommendation: THROTTLE to 100 TPS until infrastructure stabilizes. Estimated lost revenue: ₹12,000. Prevented cascade failure cost: ₹85,000+"

---

#### Scenario Category 2: Server Outage Detection

**What it is**: Complete or partial failure of payment provider infrastructure, distinct from normal transaction failures.

**Detection signals**:
- 100% failure rate for a specific provider (vs. partial failure patterns)
- Connection timeouts dominate error codes (not business declines)
- No successful transactions for 2+ minutes from a provider
- Health check endpoints returning errors or timing out

**Decision logic**:
- If single provider down with alternatives available: `FAILOVER` - immediate traffic redirect
- If multiple providers showing stress: `ALERT` - escalate to ops (potential upstream issue)
- If partial outage (specific regions/card types): `SELECTIVE_REROUTE` - targeted traffic steering
- If all providers degraded: `CIRCUIT_BREAK` - halt new transactions, protect existing sessions

**Escalation triggers**:
- Outage duration > 5 minutes → Auto-escalate to on-call team
- Outage affecting > 30% of traffic → SMS alert to leadership
- Outage during peak hours (10 AM - 10 PM) → Immediate P1 incident

**Example pattern**: "ICICI payment gateway returning connection refused errors. 100% failure rate for last 3 minutes. Health check confirmed DOWN. 47 transactions affected so far. Recommendation: FAILOVER to Axis Bank immediately. Estimated recovery time: unknown. Alert ops team for vendor communication."

---

#### Scenario Category 3: Suspicious Activity Detection

**What it is**: Patterns indicating potential fraud, bot activity, or account compromise that require security intervention rather than simple rerouting.

**Detection signals**:
- Velocity anomalies: Same card/user attempting 10+ transactions in 60 seconds
- Geographic impossibility: Transactions from distant locations within minutes
- Amount patterns: Repeated exact amounts (card testing behavior)
- Decline cycling: Same card trying multiple small amounts after large decline
- Device fingerprint anomalies: Known fraudulent device signatures
- BIN attacks: Sequential card numbers being tested

**Decision logic**:
- If isolated suspicious user: `BLOCK_USER` - temporary hold pending verification
- If card testing pattern detected: `BLOCK_CARD` - prevent further attempts, alert issuer
- If coordinated attack suspected: `RATE_LIMIT` - apply aggressive throttling to pattern
- If high-value account compromise: `ESCALATE_SECURITY` - immediate human review
- Never auto-reroute suspicious transactions (amplifies fraud exposure)

**Risk scoring**:
- Low (score < 30): Monitor only, allow transaction
- Medium (30-70): Add friction (OTP, 3DS), log for review
- High (> 70): Block and alert, require manual approval

**Example pattern**: "Card ending 4521 has attempted 23 transactions in 4 minutes, all ₹1-₹10, all declined. Classic card testing behavior. BIN indicates international card from unusual geography. Recommendation: BLOCK_CARD immediately, notify issuing bank, flag merchant account for review. Do NOT reroute - prevents fraud amplification."

---

#### Scenario Category 4: High-Risk Payment Handling

**What it is**: Legitimate transactions that carry elevated risk due to amount, merchant category, or user history, requiring additional validation before processing.

**Detection signals**:
- Transaction amount > user's historical maximum by 5x+
- First transaction from new high-risk merchant category (crypto, gambling, forex)
- Dormant account suddenly active with large transaction
- Cross-border transaction to high-risk geography
- Mismatched billing/shipping addresses
- Corporate card used for personal-category purchases

**Decision logic**:
- If risk is verifiable: `STEP_UP_AUTH` - request additional authentication
- If risk requires human judgment: `HOLD_FOR_REVIEW` - queue for manual approval
- If known good customer with unusual pattern: `SOFT_DECLINE` - decline with retry option
- If transaction matches fraud pattern but customer is VIP: `ESCALATE_PRIORITY` - expedited human review
- If regulatory requirement: `COMPLIANCE_HOLD` - mandatory review regardless of outcome

**Business rules**:
- Never auto-approve transactions > ₹50,000 from new users
- Always step-up auth for first international transaction
- Require 2FA for crypto-related merchant categories
- Hold all transactions from sanctioned geographies for compliance

**Example pattern**: "User ID 78234 (account age: 8 months, typical transaction: ₹500-₹2,000) attempting ₹75,000 purchase at cryptocurrency exchange. First crypto transaction on account. Risk score: 67. Recommendation: STEP_UP_AUTH with mandatory OTP verification. If user completes auth, proceed with transaction but flag for 24-hour review. Do not auto-decline VIP tier users."

---

### Extended Decision Types Reference

The original REROUTE/IGNORE/ALERT decisions are expanded to cover all operational scenarios:

| Decision | Use Case | When to Apply |
|----------|----------|---------------|
| `REROUTE` | Payment failure remediation | Net benefit positive, pattern is fixable via alternate provider |
| `IGNORE` | Unprofitable intervention | Reroute cost exceeds transaction margin |
| `ALERT` | Ops notification needed | Pattern requires human judgment or vendor escalation |
| `THROTTLE` | High traffic protection | System approaching capacity limits |
| `FAILOVER` | Provider outage response | Single provider down, alternatives available |
| `CIRCUIT_BREAK` | System protection | Multiple providers degraded, prevent cascade |
| `BLOCK_USER` | Suspicious activity | Individual user shows fraud patterns |
| `BLOCK_CARD` | Card compromise | Card testing or stolen card indicators |
| `RATE_LIMIT` | Attack mitigation | Coordinated abuse pattern detected |
| `STEP_UP_AUTH` | High-risk validation | Transaction requires additional verification |
| `HOLD_FOR_REVIEW` | Manual approval needed | Risk too high for automated decision |
| `ESCALATE_SECURITY` | Security team involvement | Potential account compromise or fraud ring |
| `ESCALATE_PRIORITY` | VIP handling | High-value customer requires white-glove treatment |
| `COMPLIANCE_HOLD` | Regulatory requirement | Transaction requires mandatory compliance review |

---

### CHECKPOINT 2: Validation

**What to check**:
✅ File `transactions.csv` created with exactly 1000 rows  
✅ Overall failure rate: 15-25% (realistic)  
✅ Trap 1 (HDFC Whale): 40-60 affected txns, >95% failure rate  
✅ Trap 2 (SBI Micro): 100-150 affected txns, ~75% failure rate  
✅ Trap 3 (ICICI Canary): Clear spike visible when sorted by timestamp  
✅ Trap 4 (Traffic Tsunami): 400 txns in compressed window, uniform stress  
✅ Trap 5 (Card Tester): 15-25 micro-transactions from single source  
✅ Trap 6 (Whale Alert): 5-10 high-value anomalous transactions  

**AI Review Prompt**:
```
"Step 2 complete. Here's my generator output:
[PASTE TERMINAL OUTPUT]

Sample of transactions.csv:
[PASTE FIRST 20 ROWS]

Pattern verification stats:
[PASTE PATTERN COUNTS & FAILURE RATES]

Questions:
1. Are failure rates in acceptable ranges?
2. Are patterns detectable but not trivial?
3. Any issues with data quality?"
```

**Expected AI Response**:
- Confirms all 3 patterns present and statistically significant
- Validates that Trap 2 has low margin (forcing IGNORE decision)
- Checks temporal spread for Trap 3 (spike must precede outage)

---

## STEP 3: PYDANTIC MODELS (30 minutes)

### What You're Building
Type-safe data schemas with built-in validation to prevent LLM hallucinations and enforce business rules.

### Why This Matters
LLMs can hallucinate:
- Invalid JSON structure
- Contradictory logic (saying "negative net benefit" but deciding REROUTE)
- Vague reasoning ("it's bad" instead of "₹6,627 loss")

Pydantic catches these at runtime BEFORE they pollute your dashboard.

### Required Components

#### Component 3.1: Transaction Schema
**Purpose**: Validate individual transaction records from CSV

**Required fields with constraints**:
- `transaction_id`: string
- `timestamp`: datetime object
- `bank`: enum (only 4 valid values)
- `card_type`: enum (only 3 valid values)
- `amount`: float, must be > 0
- `status`: enum (SUCCESS or FAILED)
- `latency_ms`: int, must be >= 0
- `error_code`: optional string (None if SUCCESS)

#### Component 3.2: FailureCluster Schema
**Purpose**: Represent aggregated patterns for LLM input

**Required fields**:
- `bank`: string
- `card_type`: string
- `amount_range`: string (e.g., "5000-10000")
- `count`: int (number of transactions in cluster)
- `avg_amount`: float
- `failure_rate`: float between 0.0 and 1.0
- `time_window`: string (e.g., "14:00-16:00")
- `error_codes`: list of strings

#### Component 3.3: AgentDecision Schema (CRITICAL)
**Purpose**: Validate LLM output and enforce business logic

**Required fields with validation**:

1. **pattern_detected** (string, min 20 chars)
   - Must be specific: "HDFC Rewards >₹5K, 14:00-16:00" ✅
   - Not generic: "Bank failures" ❌

2. **affected_volume** (int, >= 1)
   - Number of transactions in pattern

3. **cost_analysis** (string, min 30 chars)
   - Must contain rupee symbol (₹ or Rs)
   - Must show calculation: "Reroute: ₹15, Margin: ₹156, Net: +₹141"

4. **temporal_signal** (enum: "stable", "spike_detected", "declining")
   - Indicates if failure rate is changing

5. **decision** (enum: see Decision Types below)
   - The final action recommendation

6. **risk_category** (enum: "payment_failure", "high_traffic", "server_outage", "suspicious_activity", "high_risk_payment")
   - Classification of the detected issue type

7. **reasoning** (string, min 100 chars)
   - Business explanation, NOT technical jargon
   - FORBIDDEN words: "model", "algorithm", "neural network"
   - REQUIRED elements: specific numbers, impact in ₹

7. **confidence** (float, 0.0-1.0)
   - LLM's self-assessed certainty

**Critical Validators**:

**Validator 1: Cost Analysis Must Mention Money**
- Check if `cost_analysis` contains ₹ or Rs
- Reject if missing

**Validator 2: Decision Must Align with Cost Analysis**
- If `cost_analysis` contains "net: -" or "negative", decision CANNOT be REROUTE
- Catch contradictory logic

**Validator 3: Reasoning Quality Check**
- Reject if reasoning contains technical jargon
- Ensure business language

#### Component 3.4: PerformanceMetrics Schema
**Purpose**: Dashboard metrics

**Required fields**:
- `total_transactions`, `total_failures`: ints
- `reroutes_executed`, `reroutes_ignored`, `alerts_raised`: ints
- `total_cost`, `total_revenue_saved`, `net_profit`: floats
- `patterns_discovered`: int
- `decision_accuracy`: float (0.0-1.0)

### CHECKPOINT 3: Validation

**What to check**:
✅ `models.py` created with all 4 schemas  
✅ Test script runs and validates good decision  
✅ Test script correctly REJECTS bad decision (REROUTE with negative net)  
✅ Validators enforce rupee symbols, business language, logic consistency  

**AI Review Prompt**:
```
"Step 3 complete. Here's my models.py test output:
[PASTE TEST RESULTS]

My AgentDecision schema:
[PASTE SCHEMA CODE]

Questions:
1. Are validators comprehensive enough?
2. Any edge cases I'm missing?
3. Should I add more forbidden words?"
```

**Expected AI Response**:
- Confirms validators catch contradictions
- Suggests edge cases (e.g., what if confidence is 0.0?)
- May recommend additional checks for temporal_signal logic

---

## STEP 4: PATTERN AGENT CORE (6 hours - MOST CRITICAL)

### What You're Building
The LLM-powered brain that:
1. Aggregates failures into clusters
2. Sends clusters to GPT-4 with carefully crafted prompt
3. Receives structured decisions
4. Validates via Pydantic
5. Returns actionable insights

### Why This Matters
**This is your differentiator**. Competitors will have basic retry logic. You have AI that REASONS about patterns and EXPLAINS in business terms.

### Architecture Flow
```
transactions.csv
    ↓ Load
pandas DataFrame
    ↓ Filter failures
Failed transactions only
    ↓ Group by (bank, card_type, amount_range, time_window)
Failure clusters (aggregated view)
    ↓ Convert to JSON
Cluster summaries
    ↓ Add historical context (for Trap 3 detection)
Enriched input
    ↓ Send to LLM with system prompt
GPT-4 API call
    ↓ Parse JSON response
Raw LLM output
    ↓ Validate with Pydantic
AgentDecision object
    ↓ Store
List of decisions for dashboard
```

### Required Components

#### Component 4.1: Data Loader
**Purpose**: Read CSV and convert to pandas DataFrame

**Must do**:
- Load `transactions.csv`
- Parse `timestamp` column as datetime
- Validate schema matches Transaction Pydantic model
- Handle missing/malformed data gracefully

#### Component 4.2: Failure Cluster Aggregator
**Purpose**: Group failures into patterns for LLM analysis

**Aggregation logic**:
- Filter: `status == "FAILED"`
- Group by: `(bank, card_type)`
- Further segment by:
  - Amount range: <100, 100-1000, 1000-5000, >5000
  - Time window: hourly buckets (00:00-01:00, 01:00-02:00, etc.)

**For each cluster, calculate**:
- `count`: number of failures
- `avg_amount`: mean transaction amount
- `failure_rate`: failures / total transactions in that segment
- `error_codes`: list of unique error types
- `time_window`: temporal range (e.g., "14:00-16:00")

**Output format**: List of FailureCluster Pydantic objects

**Critical**: Include historical context for Trap 3 detection
- Example: "ICICI Debit failure rate 1 hour ago: 5%, now: 18%"

#### Component 4.3: LLM System Prompt (THE MOST IMPORTANT TEXT)

**Purpose**: Instruct GPT-4 to think like a fintech operations analyst

**Required sections**:

**Section 1: Identity**
```
You are a Payment Operations AI for a fintech platform.
Your job: Decide if payment failures are worth fixing.
You are NOT a "fix everything" bot. You are a PROFIT optimizer.
```

**Section 2: Business Constraints**
```
- Reroute Fee: ₹15.00 (fixed cost per transaction)
- Margin: 2.0% of transaction amount
- You only intervene when margin > cost
```

**Section 3: Reasoning Framework**
```
For each failure cluster, analyze FIVE dimensions:

1. PATTERN DETECTION
   - Is this isolated or systemic?
   - What's the specific segment? (bank + card + amount + time)
   - Is this a single-provider issue or system-wide stress?
   - Example: "HDFC Rewards >₹5K failing at 2PM" = pattern
   - Example: "Random HDFC failures" = noise
   - Example: "All providers slow simultaneously" = traffic surge

2. COST-BENEFIT ANALYSIS
   Calculate:
     Potential_Revenue = avg_amount × 0.02 × count
     Intervention_Cost = 15.00 × count
     Net_Benefit = Potential_Revenue - Intervention_Cost
   
   Decision Rules:
     IF Net_Benefit < 0: IGNORE (let it fail, save money)
     IF Net_Benefit > 0 AND pattern is fixable: REROUTE
     IF Net_Benefit > 0 BUT root cause is bank-side: ALERT

3. TEMPORAL REASONING
   - Is failure rate stable, spiking, or declining?
   - Example: "ICICI Debit: 5% → 18% in 10 min" = spike
   - Spike = early warning of total outage
   - Action: ALERT (don't waste money rerouting doomed traffic)

4. TRAFFIC & CAPACITY ANALYSIS
   - Is overall transaction volume normal or elevated?
   - Are multiple providers showing stress simultaneously?
   - Is latency increasing uniformly across all endpoints?
   
   Decision Rules:
     IF single provider down: FAILOVER to alternate
     IF all providers stressed: THROTTLE incoming traffic
     IF system at capacity: CIRCUIT_BREAK to prevent cascade

5. SECURITY & RISK ASSESSMENT
   - Does pattern indicate fraud (velocity, amount patterns)?
   - Is transaction risk elevated (amount anomaly, new category)?
   - Does user behavior match known attack patterns?
   
   Decision Rules:
     IF card testing detected: BLOCK_CARD + ESCALATE_SECURITY
     IF high-risk transaction: STEP_UP_AUTH or HOLD_FOR_REVIEW
     IF account compromise suspected: BLOCK_USER + ESCALATE_PRIORITY
```

**Section 4: Output Format**
```
Return STRICT JSON matching AgentDecision schema:
{
  "pattern_detected": "Specific segment description",
  "affected_volume": 47,
  "cost_analysis": "Reroute: ₹15 × 47 = ₹705. Revenue: ₹156 × 47 = ₹7,332. Net: +₹6,627",
  "temporal_signal": "stable" | "spike_detected" | "declining",
  "decision": "REROUTE" | "IGNORE" | "ALERT",
  "reasoning": "Detailed business explanation with numbers",
  "confidence": 0.94
}
```

**Section 5: Examples (Few-Shot Learning)**

**Good Example 1**:
```json
{
  "pattern_detected": "HDFC Rewards >₹5,000 failing during 14:00-16:00 window",
  "affected_volume": 47,
  "cost_analysis": "Reroute cost: ₹705 (47 × ₹15). Revenue saved: ₹7,332 (47 × ₹156 avg margin). Net: +₹6,627",
  "temporal_signal": "stable",
  "decision": "REROUTE",
  "reasoning": "High-value Rewards card segment showing 98% failure rate in afternoon window. Each transaction has substantial margin (avg ₹7,842 amount = ₹156 margin). Total impact if pattern continues: ₹6,627 profit. Clear systemic issue, not random failures. Reroute to Axis Bank.",
  "confidence": 0.94
}
```

**Good Example 2**:
```json
{
  "pattern_detected": "SBI micro-transactions <₹100",
  "affected_volume": 127,
  "cost_analysis": "Reroute cost: ₹1,905 (127 × ₹15). Revenue saved: ₹254 (127 × ₹2 avg margin). Net: -₹1,651",
  "temporal_signal": "stable",
  "decision": "IGNORE",
  "reasoning": "Small-value transactions with average amount ₹42. Margin per transaction is only ₹0.84, while rerouting costs ₹15. This creates a net loss of ₹14.16 per transaction. Total impact: -₹1,651 if we intervene. Better to let these fail and preserve capital for high-value interventions.",
  "confidence": 0.89
}
```

**Good Example 3**:
```json
{
  "pattern_detected": "ICICI Debit failure rate spike: 5% → 18% in 10 minutes",
  "affected_volume": 23,
  "cost_analysis": "Reroute cost: ₹345 (23 × ₹15). However, spike indicates imminent total outage.",
  "temporal_signal": "spike_detected",
  "decision": "ALERT",
  "reasoning": "ICICI Debit card failures have tripled in the last 10 minutes from baseline 5% to 18%. This is a classic early warning signal of infrastructure failure. Historical data shows spikes precede total outages by 20-40 minutes. Rerouting now would waste ₹345 as the backup provider will likely fail too. Recommendation: ALERT operations team to investigate root cause and prepare for potential full ICICI outage.",
  "confidence": 0.76
}
```

**Bad Example (What NOT to do)**:
```json
{
  "pattern_detected": "Errors detected",  ❌ Too vague
  "reasoning": "The model identified anomalies in the data"  ❌ Technical jargon
}
```

**Good Example 4 (Traffic Surge)**:
```json
{
  "pattern_detected": "System-wide traffic surge: 180 TPS vs. normal 50 TPS, all providers stressed",
  "affected_volume": 234,
  "cost_analysis": "Rerouting futile - all 4 providers showing 2000ms+ latency. Throttling to 100 TPS loses ~₹12,000 in transactions but prevents ₹85,000+ cascade failure.",
  "temporal_signal": "spike_detected",
  "risk_category": "high_traffic",
  "decision": "THROTTLE",
  "reasoning": "Flash sale event causing 3.6x normal transaction volume. All payment providers showing uniform stress - HDFC, SBI, ICICI, Axis all at 2000ms+ latency with climbing error rates. This is not a single-provider issue; rerouting would simply move load between equally stressed systems. Implementing 50% throttle to reduce TPS from 180 to 100. Priority queue for VIP customers. Estimated transaction loss: ₹12,000. Prevented cascade outage value: ₹85,000+. Resume full capacity in 15 minutes.",
  "confidence": 0.88
}
```

**Good Example 5 (Card Testing Attack)**:
```json
{
  "pattern_detected": "Card testing attack: 23 micro-transactions (₹1-₹10) from single card in 4 minutes",
  "affected_volume": 23,
  "cost_analysis": "Margin on these transactions: ₹2.30 total. However, this is fraud pattern - security cost of NOT blocking far exceeds revenue.",
  "temporal_signal": "spike_detected",
  "risk_category": "suspicious_activity",
  "decision": "BLOCK_CARD",
  "reasoning": "Card ending 4521 has attempted 23 transactions in 4 minutes, all ₹1-₹10 amounts, 22 declined. This is textbook card testing behavior - fraudster validating stolen card before large purchase. BIN indicates international card from high-risk geography. Normal cost-benefit would say IGNORE (negative margin), but security requires immediate BLOCK. Notifying issuing bank. Flagging merchant account for review. Blocking prevents ₹50,000+ potential fraud loss if card is validated.",
  "confidence": 0.92
}
```

**Good Example 6 (High-Risk Transaction)**:
```json
{
  "pattern_detected": "Anomalous high-value transaction: ₹75,000 from user with ₹2,000 typical spend",
  "affected_volume": 1,
  "cost_analysis": "Transaction margin: ₹1,500. However, risk profile requires additional verification before approval.",
  "temporal_signal": "stable",
  "risk_category": "high_risk_payment",
  "decision": "STEP_UP_AUTH",
  "reasoning": "User ID 78234 (8-month account, typical transaction ₹500-₹2,000) attempting ₹75,000 at cryptocurrency exchange. This is their first crypto transaction ever. Transaction is 37x their historical average. While user is legitimate tier-2 member with good standing, risk score of 67 requires step-up authentication. Requesting OTP verification. If completed successfully, approve with 24-hour review flag. Do not auto-decline - this may be legitimate investment, and declining VIP users damages retention.",
  "confidence": 0.79
}
```

#### Component 4.4: LLM Integration
**Purpose**: Call OpenAI API with proper error handling

**Must include**:
- LangChain ChatOpenAI wrapper
- JsonOutputParser to enforce structure
- Retry logic (if API fails, retry max 2 times)
- Timeout handling (5 seconds max per call)
- Token counting (stay under MAX_TOKENS from config)

**Input preparation**:
- Take list of FailureCluster objects
- Convert to JSON string
- Truncate if >2000 tokens (keep only top clusters by volume)
- Add historical context for temporal reasoning

**Output handling**:
- Parse JSON response
- Validate with AgentDecision Pydantic model
- If validation fails, log error and retry with stronger prompt
- If 2 retries fail, use fallback decision: `IGNORE` with low confidence

#### Component 4.5: Batch Processor
**Purpose**: Analyze all failure clusters and collect decisions

**Must do**:
- Iterate through all clusters
- For each cluster, call LLM
- Collect AgentDecision objects
- Calculate aggregate metrics (total cost, total revenue, net profit)
- Return both individual decisions and summary metrics

### CHECKPOINT 4: Validation

**What to check**:
✅ `pattern_agent.py` created with all components  
✅ Can load `transactions.csv` successfully  
✅ Aggregation produces 3-10 failure clusters (not 100, not 1)  
✅ LLM successfully identifies Trap 1 (HDFC Whale) → REROUTE decision  
✅ LLM successfully identifies Trap 2 (SBI Micro) → IGNORE decision  
✅ LLM successfully identifies Trap 3 (ICICI Spike) → ALERT decision  
✅ All decisions pass Pydantic validation  
✅ Net profit is positive (>₹500)  

**AI Review Prompt**:
```
"Step 4 complete. Here's my pattern_agent.py execution:
[PASTE TERMINAL OUTPUT]

Decisions generated:
[PASTE JSON OF 3-5 DECISIONS]

Metrics:
[PASTE NET PROFIT, ACCURACY, ETC.]

Questions:
1. Did the LLM find all 3 traps?
2. Are cost calculations correct?
3. Is reasoning quality good?
4. Any hallucinations detected?"
```

**Expected AI Response**:
- Confirms all 3 patterns detected correctly
- Validates math: Net profit = Revenue - Costs
- Checks reasoning quality (specific numbers, business language)
- Flags any suspicious outputs (generic reasoning, wrong decisions)

---

## STEP 5: ACTION EXECUTOR - Real Execution Layer (3 hours) ⭐

### What You're Building
The execution layer that takes LLM decisions and **actually performs actions**. Not just recommendations - real execution with proof.

**Execution Strategy**:
- ✅ **Email alerts**: REAL (use SMTP or SendGrid to send actual emails)
- ✅ **File system logs**: REAL (write to `execution_log.json` with timestamps)
- ✅ **Payment reroutes**: SIMULATED (mock gateway with realistic responses)
- ✅ **Database updates**: REAL (SQLite or JSON file showing transaction status changes)

### Required Action Tools

#### Tool 5.1: EmailAlertTool
**Purpose**: Send REAL email alerts for patterns requiring ops intervention

**Must do**:
- Accept: pattern_name, severity (LOW/MEDIUM/HIGH/CRITICAL), affected_count, recommended_action
- **Actually send email** via SMTP to configured ops email address
- Email subject: `[SENTINEL ALERT] {severity}: {pattern_name}`
- Email body: Include pattern details, affected volume, cost analysis, recommended action
- Log send status to `email_log.json` (success/failure, timestamp, recipient)
- Handle failures gracefully (retry once, then log failure)

**Demo value**: Judges see real email arrive during presentation!

#### Tool 5.2: RerouteSimulator
**Purpose**: Simulate rerouting failed transactions to backup payment gateway

**Must do**:
- Accept transaction IDs and target gateway
- Simulate API call with realistic latency (200-500ms delay)
- Return success/failure (90% success rate for simulation)
- **Write to execution_log.json**: {txn_id, original_gateway, backup_gateway, result, timestamp, cost_incurred}
- Calculate and return: transactions_rerouted, success_count, total_cost, revenue_recovered

**Demo value**: Shows instant decision execution with detailed logs

#### Tool 5.3: ConfigUpdater
**Purpose**: Update routing rules to block unprofitable patterns

**Must do**:
- Accept pattern (e.g., "SBI <₹100") and action ("SKIP_REROUTE")
- **Write to routing_config.json**: Add rule blocking future reroutes for this pattern
- Log configuration change with timestamp and reason
- Calculate estimated savings from future prevention

**Demo value**: Shows learning capability (system improves itself)

#### Tool 5.4: DatabaseLogger
**Purpose**: Track all agent decisions and their outcomes

**Must do**:
- Write every decision to `decisions.db` (SQLite) or `decisions.json`
- Schema: {decision_id, timestamp, pattern, action_taken, affected_count, cost, revenue, net_profit, confidence, reasoning}
- Enable querying for dashboard display

**Demo value**: Provides audit trail (judges can inspect every decision)

**Must do**:
- Accept transaction filter criteria (amount, velocity, geography)
- Block matching transactions for review
- Log block reason and affected volume

#### Tool 5.5: EscalateTool
**Purpose**: Escalate patterns requiring immediate human review

**Must do**:
- Accept urgency level and contact method
- Include full pattern context and recommended actions
- Track escalation response time

---

## STEP 6: BASELINE COMPARISON (1 hour)

### What You're Building
A "naive" retry-everything system to prove SENTINEL's superiority.

### Why This Matters
**You need a villain**. Without a baseline, your ₹800 profit means nothing. With a baseline that LOSES ₹2,250, your system looks brilliant.

### Required Components

#### Component 5.1: Naive Agent
**Purpose**: Simulate competitor's approach

**Logic**:
```
FOR each failed transaction:
  ALWAYS reroute (no intelligence)
```

**Calculations**:
- Total failures: ~200 (from your dataset)
- Reroutes: 200 (all of them)
- Cost: 200 × ₹15 = ₹3,000
- Revenue saved: Sum of (amount × 0.02) for all failures
- Net profit: Revenue - Cost (usually negative)

#### Component 5.2: Metrics Comparison
**Must track**:
| Metric | Naive System | SENTINEL | Delta |
|--------|--------------|----------|-------|
| Reroutes | 200 | ~50 | -75% |
| Cost | ₹3,000 | ₹750 | -75% |
| Revenue | ₹800 | ₹800 | 0% |
| Net Profit | -₹2,200 | +₹50 | +₹2,250 |

**Key insight**: Same revenue, but 10x better cost efficiency

### CHECKPOINT 5: Validation

**What to check**:
✅ Safety validator correctly identifies unsafe decisions  
✅ Phidata agent successfully calls custom tools  
✅ Executor can REFUSE Council decisions (test with low confidence decision)  
✅ Execution results contain detailed logs  
✅ Net impact calculations are correct  
✅ SafetyOverride objects are created when appropriate  

**AI Review Prompt**:
```
"Step 5 complete. Comparison results:
[PASTE COMPARISON TABLE]

Does this clearly show SENTINEL's advantage?
Is the story compelling?"
```

---

## STEP 6: STREAMLIT DASHBOARD (4 hours)

### What You're Building
A visual interface that tells the before/after story and displays pattern discoveries.

### Why This Matters
Judges see the dashboard for 3 minutes. It must immediately communicate:
1. The problem (naive system wastes money)
2. The solution (SENTINEL finds patterns)
3. The impact (₹X,XXX saved)

### Required Components

#### Component 6.1: Dashboard Layout
**Structure**:
```
┌─────────────────────────────────────────┐
│ SENTINEL Operations Center       [LIVE] │
├─────────────────────────────────────────┤
│ 📊 Performance Metrics (3 columns)      │
│ [Net Profit] [Patterns] [Decisions]     │
├─────────────────────────────────────────┤
│ 🎯 Pattern Discovery (expandable cards) │
│ • Pattern 1 details                      │
│ • Pattern 2 details                      │
│ • Pattern 3 details                      │
├─────────────────────────────────────────┤
│ 🧠 Latest Agent Reasoning (text box)    │
│ Full explanation of most recent decision │
├─────────────────────────────────────────┤
│ 📈 Comparative Analysis (chart)         │
│ SENTINEL vs Naive Baseline               │
└─────────────────────────────────────────┘
```

#### Component 6.2: Top Metrics Bar
**Must display** (large numbers, green/red coloring):
- Net Profit: `+₹847` (green if positive, red if negative)
- Patterns Discovered: `3`
- Total Decisions: `89`

#### Component 6.3: Pattern Discovery Cards
**For each discovered pattern, show**:
- Pattern name: "HDFC Whale" / "SBI Micro-Loss" / "ICICI Canary"
- Description: "HDFC Rewards >₹5K failing 14:00-16:00"
- Affected volume: "47 transactions"
- Action taken: "REROUTE" / "IGNORE" / "ALERT" (with color coding)
- Impact: "Saved ₹6,627" or "Avoided waste of ₹1,651"

**Color coding**:
- Green: Profitable reroute executed
- Red: Unprofitable fix avoided (smart IGNORE)
- Orange: Alert raised (ops intervention needed)

#### Component 6.4: Agent Reasoning Display
**Show**:
- Full text from `reasoning` field of latest decision
- Confidence score as percentage
- Timestamp

**Purpose**: Prove explainability (no black boxes)

#### Component 6.5: Comparative Analysis Chart
**Chart type**: Side-by-side bar chart

**Metrics to compare**:
- Reroutes: SENTINEL (47) vs Baseline (200)
- Cost: SENTINEL (₹705) vs Baseline (₹3,000)
- Net Profit: SENTINEL (+₹847) vs Baseline (-₹2,200)

**Critical element**: Large callout showing ₹ saved

#### Component 6.6: Live Bank Status Monitor ⭐ **CRITICAL FOR DEMO**
**Purpose**: Show real-time health of each payment provider

**Must display** (4 columns, one per bank):
- **Bank name**: HDFC, SBI, ICICI, Axis
- **Success rate**: 98% (color-coded: 🟢 >90%, 🟡 70-90%, 🔴 <70%)
- **Transaction throughput**: "347 TPS" (transactions per second)
- **Latency**: "245ms" (response time)
- **Status indicator**: Visual dot showing health

**Visual design**:
```
┌──────────┐
│   HDFC   │
│  🟢 98%  │  ← Big number, color changes
│  347 TPS │  ← Real-time counter
│ ⚡ 245ms  │  ← Lightning bolt + latency
└──────────┘
```

**Update frequency**: Every 1 second (use `st.empty()` containers)

**Demo value**: Judges WATCH banks turn red when patterns emerge, then recover when agent reroutes

---

#### Component 6.7: Live Transaction Feed ⭐ **THE WOW FACTOR**
**Purpose**: Show transactions being processed and rerouted in real-time

**Must display**:
- **Scrolling log** of last 15 transactions (newest at top)
- **Transaction details**: ID, original bank, amount, outcome
- **Reroute visualization**: "HDFC → Axis" with arrow animation
- **Status badges**: ✅ SUCCESS, ❌ FAILED, ⚙️ REROUTING, 🚫 IGNORED

**Entry format**:
```
14:32:15 TXN04523 HDFC→AXIS ₹7,842 ✅ REROUTED (saved ₹141)
14:32:14 TXN04522 HDFC→AXIS ₹9,234 ✅ REROUTED (saved ₹169)
14:32:13 TXN04521 SBI ₹42 🚫 IGNORED (unprofitable)
14:32:11 🚨 ALERT: HDFC Rewards pattern detected!
14:32:10 TXN04520 ICICI ₹1,234 ✅ SUCCESS
```

**Visual effects**:
- New entries **fade in** from top
- Rerouted transactions **pulse green** for 2 seconds
- Ignored transactions show **red strikethrough**
- Pattern alerts show **yellow background** with 🚨 icon

**Demo value**: Judges see LIVE proof that agent is taking actions, not just recommending

---

#### Component 6.8: Agent Action Theater ⭐ **THE EXPLAINER**
**Purpose**: Show Council → Executor decision flow in real-time

**Layout** (2 sections side-by-side):

**Left: Council Reasoning**
```
┌─────────────────────────────────┐
│ 🧠 COUNCIL AGENT                │
├─────────────────────────────────┤
│ Pattern: HDFC Rewards >₹5K      │
│ Affected: 47 transactions       │
│ Cost: ₹705 | Revenue: ₹7,332    │
│ Net: +₹6,627                    │
│                                 │
│ Decision: REROUTE               │
│ Confidence: 94%                 │
│                                 │
│ Reasoning: High-value Rewards   │
│ card segment showing 98%        │
│ failure rate...                 │
└─────────────────────────────────┘
```

**Right: Executor Actions**
```
┌─────────────────────────────────┐
│ ⚙️ EXECUTOR AGENT               │
├─────────────────────────────────┤
│ ✅ Validating decision...       │
│ ✅ Confidence check: PASS       │
│ ✅ Net benefit check: PASS      │
│ ✅ Capacity check: PASS         │
│                                 │
│ 🔄 Executing reroute...         │
│ ├─ Target: Axis Bank            │
│ ├─ Transactions: 47             │
│ └─ Status: 45/47 SUCCESS (96%)  │
│                                 │
│ ✅ EXECUTION COMPLETE           │
│ Saved: ₹6,627                   │
└─────────────────────────────────┘
```

**Update flow**:
1. Council section populates (shows LLM reasoning)
2. Executor section shows validation checks (one by one, with delays)
3. Executor section shows execution progress bar
4. Final success message with savings

**Demo value**: Shows the AI "thinking" and the agent "acting" - full transparency

---

#### Component 6.9: Simulation Controller
**Purpose**: Control demo playback for presentation

**Controls**:
- ▶️ **Play button**: Start processing transactions
- ⏸️ **Pause button**: Freeze at current state
- ⏭️ **Skip to pattern**: Jump to next interesting event
- 🔄 **Reset**: Reload data and restart
- **Speed slider**: 1x, 2x, 5x, 10x (for demo rehearsal)

**Auto-pause triggers**:
- When major pattern detected (give time to explain)
- When agent executes action (show the moment)
- When metrics update significantly

**Demo value**: Control the narrative - pause at key moments to explain to judges

---

#### Component 6.10: Side-by-Side Comparison (Enhanced)
**Purpose**: Show before/after with LIVE updates

**Layout**:
```
┌──────────────────┬──────────────────┐
│  Naive System    │   SENTINEL       │
├──────────────────┼──────────────────┤
│ Reroutes: 200    │ Reroutes: 47     │ ← Updates live
│ Cost: ₹3,000     │ Cost: ₹705       │ ← Counter animates
│ Net: -₹2,200 🔴  │ Net: +₹6,627 🟢  │ ← Big number, colored
└──────────────────┴──────────────────┘
```

**Visual effects**:
- Numbers **count up** as transactions process
- Net profit turns **green** when positive
- Sparkline charts show trend over time
- **Final reveal**: Total savings number explodes on screen

**Demo value**: Judges see gap widening in real-time - immediate proof of superiority

---

### CHECKPOINT 6: Validation

**What to check**:
✅ Dashboard runs: `streamlit run dashboard.py`  
✅ All metrics display correctly  
✅ Live bank monitor showing 4 banks with real-time stats  
✅ Transaction feed scrolling with reroute animations  
✅ Agent Action Theater showing Council + Executor flow  
✅ Pattern cards visible and properly formatted  
✅ Comparison chart shows clear advantage  
✅ Simulation controls work (Play/Pause/Reset)  
✅ No errors in console  
✅ Looks professional (not cluttered)  

**AI Review Prompt**:
```
"Step 6 complete. Screenshot of dashboard:
[PASTE SCREENSHOT OR DESCRIBE LAYOUT]

Live demo features:
[DESCRIBE BANK MONITOR, TRANSACTION FEED, ACTION THEATER]

Questions:
1. Is the live simulation smooth and compelling?
2. Can judges SEE the agent taking actions?
3. Too cluttered or too sparse?
4. Any UI improvements?"
```

---

## STEP 6.5: DEMO CHOREOGRAPHY ⭐ **THE WINNING STRATEGY**

### The 3-Minute Pitch That Wins

#### Pre-Demo Setup (30 seconds before judges arrive)
1. Load dashboard with simulation PAUSED at interesting moment
2. Have 4 banks showing (HDFC at 35% success rate - red)
3. Transaction feed showing recent failures
4. Council Agent box showing pattern detection in progress
5. **Position**: "This is what's happening RIGHT NOW..."

---

#### Act 1: The Problem (0:00 - 0:45)

**What judges see**:
- Static comparison chart: "Naive systems lose ₹2,250"
- Explain: "Competitors blindly retry everything. We're different."

**What you say**:
> "Most payment systems waste money fixing failures that aren't worth fixing.  
> Let me show you our AI making intelligent decisions in real-time."

**Action**: Click ▶️ Play button

---

#### Act 2: Pattern Detection (0:45 - 1:30) ⭐ **THE HOOK**

**What judges see**:
1. Transactions flowing through feed
2. **HDFC bank turns red** (success rate: 98% → 35%)
3. **🚨 Alert appears**: "HDFC Rewards pattern detected"
4. **Council Agent box populates**:
   ```
   Pattern: HDFC Rewards >₹5K @ 14:00-16:00
   Affected: 47 transactions
   Cost Analysis: Net benefit +₹6,627
   Decision: REROUTE
   Confidence: 94%
   ```

**What you say** (while pointing at screen):
> "Watch this. HDFC just started failing for high-value Rewards cards.  
> Our AI Council detected it instantly - 47 transactions, ₹6,627 potential savings.  
> But here's the key: we don't just recommend. We execute."

**Action**: Pause for 3 seconds (let judges absorb the Council reasoning)

---

#### Act 3: Agent Takes Action (1:30 - 2:15) ⭐ **THE WOW MOMENT**

**What judges see**:
1. **Executor Agent box activates**:
   ```
   ✅ Validating decision...
   ✅ Confidence check: PASS (94% > 70%)
   ✅ Net benefit check: PASS (+₹6,627 > 0)
   ✅ Capacity check: PASS (Axis Bank available)
   
   🔄 Executing reroute...
   ├─ Target: Axis Bank
   ├─ Transactions: 47
   └─ Status: [████████░░] 45/47 SUCCESS
   ```

2. **Transaction feed shows live reroutes**:
   ```
   14:32:15 TXN04523 HDFC→AXIS ₹7,842 ✅ REROUTED
   14:32:14 TXN04522 HDFC→AXIS ₹9,234 ✅ REROUTED
   14:32:13 TXN04521 HDFC→AXIS ₹6,123 ✅ REROUTED
   ```

3. **Bank columns update**:
   - HDFC: Traffic decreases (347 TPS → 290 TPS)
   - Axis: Traffic increases (289 TPS → 346 TPS)

4. **Metrics counter animates**:
   - Net profit: ₹0 → ₹6,627 (green, counting up)

**What you say** (pointing at screen excitedly):
> "There! The agent just rerouted 47 transactions to Axis Bank.  
> Watch the transaction feed - you can SEE each one succeeding.  
> And look at the bank columns - traffic shifted in real-time.  
> 45 out of 47 recovered. That's ₹6,627 saved in 10 seconds."

**Action**: Let simulation run for 5 more seconds (show more patterns if time)

---

#### Act 4: The Proof (2:15 - 2:45)

**What judges see**:
- Click on "SBI Micro-transactions" pattern card
- Shows Council decided: **IGNORE** (negative margin)
- Transaction feed shows:
  ```
  14:32:20 TXN04530 SBI ₹42 🚫 IGNORED (unprofitable)
  ```

**What you say**:
> "But here's what makes us smart: We also IGNORE unprofitable fixes.  
> These SBI micro-transactions? Margin is ₹0.84, reroute costs ₹15.  
> Our AI said 'Let it fail' - saved ₹1,651 by NOT wasting money."

**Action**: Point at comparison chart

---

#### Act 5: The Knockout (2:45 - 3:00)

**What judges see**:
- Side-by-side comparison updating live
- Final numbers reveal:
  ```
  Naive System    │   SENTINEL
  ────────────────┼──────────────
  Reroutes: 200   │ Reroutes: 47
  Cost: ₹3,000    │ Cost: ₹705
  Net: -₹2,200 🔴 │ Net: +₹6,627 🟢
  
  SENTINEL is 400% MORE PROFITABLE
  ```

**What you say** (final punch):
> "In 3 minutes, you watched our agent:
> 1. Detect patterns competitors would miss
> 2. Calculate profit in real-time
> 3. Execute actions autonomously
> 4. Turn a ₹2,200 loss into a ₹6,627 profit.
> 
> That's not a chatbot. That's agentic AI."

**Action**: Pause simulation, show `execution_log.json` if judges ask for proof

---

### Backup Demo Moments (If Judges Interrupt)

**If they ask**: "How do you know the agent actually did something?"
**Response**: 
- Open `execution_log.json` → Show timestamped reroutes
- Open email inbox → Show alert emails that arrived during demo
- Show `decisions.json` → Full audit trail with reasoning

**If they ask**: "What if the LLM is wrong?"
**Response**:
- Point to Executor validation checks
- Show SafetyOverride section: "If confidence < 70%, agent refuses"
- Demonstrate by manually setting confidence to 0.65 → Show refusal

**If they ask**: "How is this different from a rule engine?"
**Response**:
- "Rules can't detect 4-dimensional patterns like 'HDFC Rewards >₹5K @ 14:00'"
- Show weekend VIP pattern: "No SQL query finds this - requires reasoning"
- Point to Council reasoning text: "This is natural language explanation, not code"

---

### Technical Implementation Notes

**For the live simulation to work**:
1. **Process transactions in batches**: 10-20 at a time (not all 2500 at once)
2. **Add artificial delays**: 0.5 seconds between batches (makes it watchable)
3. **Auto-pause on patterns**: When pattern detected, pause for 2 seconds
4. **Smooth animations**: Use CSS transitions for bank stat changes
5. **Sound effects** (optional): Subtle "ping" when reroute succeeds

**Streamlit tricks for smooth UI**:
```python
# Use st.empty() containers for live updates
bank_status = st.empty()
transaction_feed = st.empty()
agent_actions = st.empty()

# Update in loop
for batch in transaction_batches:
    bank_status.write(get_bank_stats())
    transaction_feed.write(get_recent_txns())
    time.sleep(0.5)  # Watchable speed
```

---

### CHECKPOINT 6.5: Rehearsal Validation

## STEP 7: FINAL INTEGRATION & TESTING (3 hours)

### What You're Building
End-to-end workflow that runs from data generation → analysis → dashboard display.

### Required Components

#### Component 7.1: Main Execution Script
**Purpose**: Orchestrate entire pipeline

**Workflow**:
```python
1. Generate data (chaos_engine.py)
2. Load transactions
3. Run pattern agent analysis
4. Calculate metrics
5. Launch dashboard
```

#### Component 7.2: Error Handling
**Must handle**:
- Missing CSV file
- LLM API failures
- Invalid JSON from LLM
- Pydantic validation errors
- Streamlit crashes

**For each error**: Log clearly and provide fallback

#### Component 7.3: End-to-End Test Cases

**Test Case 1: Happy Path**
- Generate data → Analyze → Dashboard displays 3 patterns
- Expected: Net profit >₹500, all 3 traps detected

**Test Case 2: LLM Hallucination**
- Mock LLM response with invalid JSON
- Expected: System logs error, uses fallback decision, continues

**Test Case 3: Empty Dataset**
- Create CSV with 0 failures
- Expected: Dashboard shows "No patterns detected", no crashes

**Test Case 4: API Key Missing**
- Remove .env file
- Expected: Clear error message, does not crash mysteriously

#### Safety Testing Requirements

**Test Case 5: Safety Guardrail Test**
- Manually create a Council decision with confidence = 0.65 (below 0.70 threshold)
- Expected: Executor REFUSES to execute
- Verify: SafetyOverride object is created with correct reasoning

**Test Case 6: Negative ROI Test**
- Create a decision for "Margin Destroyer" pattern (net benefit < 0)
- Expected: Either Council recommends IGNORE, or Executor refuses REROUTE
- Verify: No money is wasted on unprofitable patterns

**Test Case 7: Council-Executor Agreement**
- Run with "Cascading Whale" pattern
- Expected: Council recommends REROUTE, Executor executes successfully
- Verify: Both layers agree on high-value, high-confidence patterns

### CHECKPOINT 7: Validation

**What to check**:
✅ Can run entire pipeline with one command  
✅ All 3 patterns detected consistently  
✅ Net profit matches expected range (₹500-₹1,500)  
✅ Error handling works (test with missing .env)  
✅ Dashboard updates correctly  
✅ No crashes after 5 consecutive runs  

**AI Review Prompt**:
```
"Step 7 complete. Final test results:
[PASTE 3 RUN OUTPUTS]

Questions:
1. Is this production-ready for demo?
2. Any edge cases I missed?
3. Performance issues?"
```

---

## TROUBLESHOOTING GUIDE

### Common Issues & Fixes

**Issue**: LLM returns generic reasoning
**Fix**: Strengthen system prompt with more examples, increase temperature to 0.1

**Issue**: Pydantic validation keeps failing
**Fix**: Add retry logic with modified prompt: "Your previous answer was rejected. Be more specific."

**Issue**: Net profit is negative
**Fix**: Check REROUTE_COST in config (should be 15.00, not 150.00)

**Issue**: Dashboard is slow
**Fix**: Cache LLM responses using st.cache_data

**Issue**: Patterns not detected
**Fix**: Increase failure rates in chaos_engine (make traps more obvious)

---

## SUCCESS CRITERIA SUMMARY

Your project is demo-ready when:

✅ **Data Quality**: 2500 transactions, 4 clear patterns, ~200 failures (8% rate)
✅ **Pattern Detection**: LLM finds all 4 traps consistently (whale, margin_destroyer, canary, weekend_vip)
✅ **Preprocessing**: Python aggregates 2500 rows → 10-15 clusters, LLM sees summaries only
✅ **Decision Variety**: Uses REROUTE, IGNORE, ALERT appropriately per pattern type
✅ **Decision Quality**: >85% accuracy, no contradictory logic
✅ **Explainability**: Every decision has 100+ word business reasoning
✅ **Financial Impact**: Net profit >₹800, baseline loses ₹2,250 (300%+ improvement)
✅ **Action Execution**: Agent sends REAL emails (not just logs "would send")
✅ **Execution Logs**: `execution_log.json` shows all actions taken with timestamps
✅ **Simulated Gateway**: Reroute simulator provides realistic responses with cost tracking
✅ **File System Proof**: Config files updated, decisions logged to database/JSON
✅ **Live Bank Monitor**: 4-column view showing real-time success rates, TPS, latency per bank
✅ **Live Transaction Feed**: Scrolling log showing reroutes happening (HDFC→Axis with timestamps)
✅ **Visual Proof**: Judges WATCH bank stats change as agent reroutes traffic
✅ **Agent Action Theater**: Council reasoning + Executor validation displayed in real-time
✅ **UI Clarity**: Dashboard shows live action feed ("Email sent at 14:32:15")
✅ **Reliability**: Runs 10 times without crash
✅ **Demo-Readiness**: <3 minute pitch with live simulation, judges SEE reroutes happening  

---

## FINAL WORDS FROM YOUR AI COPILOT

At each step, I'll be here to:
- Review your code against these requirements
- Catch logic errors before they become bugs
- Suggest optimizations
- Validate that you're on the winning path

When you paste code for review, I'll check:
1. **Correctness**: Does it match the spec?
2. **Completeness**: Any missing components?
3. **Quality**: Is reasoning good? Are numbers right?
4. **Demo-Readiness**: Will this impress judges?

Remember: The goal isn't perfect code. The goal is a working demo that tells an irresistible story.

Now go build SENTINEL. You've got 16 hours.

**Let's win this thing.**