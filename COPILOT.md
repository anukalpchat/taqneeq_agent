# SENTINEL BUILD COPILOT
## Your AI Pair Programmer's Master Blueprint

**PURPOSE**: This document provides your IDE's LLM (Cursor/Copilot/Codeium/Claude) with complete context to guide you through building SENTINEL. At each step, your AI can review your implementation, validate outputs, and ensure you're on the winning path.

**HOW TO USE THIS**:
1. Feed this ENTIRE document to your AI assistant at project start
2. At each CHECKPOINT, share your code/output and ask: "Review my Step X - does this meet the requirements?"
3. Your AI will validate against success criteria and catch issues early

---

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

#### 2. Profit-Aware Logic (The Business Value)
- Formula: `Net_Benefit = (Transaction_Amount × 2%) - ₹15_Reroute_Cost`
- If Net_Benefit < 0 → Let it fail (don't waste money)
- If Net_Benefit > 0 → Reroute (profitable intervention)

#### 3. Explainable Decisions (The Trust Factor)
- Every action has a reasoning: "47 transactions × ₹141 net = ₹6,627 savings"
- No black boxes: Judges must understand WHY the AI chose to act/ignore

### Success Metrics (The Scoreboard)
| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Net Profit | +₹800 | Baseline loses ₹2,250. We prove 300%+ improvement |
| Patterns Found | 3/3 | Proves AI intelligence vs. rule-based systems |
| Decision Accuracy | >85% | Shows reliability (not just luck) |
| Demo Clarity | <3 min | Must tell compelling before/after story |

### Tech Stack
- **Core**: Python 3.10+, Pandas, NumPy
- **AI**: OpenAI GPT-4 via LangChain, Pydantic validation
- **UI**: Streamlit (fastest to build, good enough for demos)
- **Data**: Synthetic (we control the patterns)

### System Architecture
```
┌─────────────────────┐
│   CHAOS ENGINE      │  Step 1-2: Generate 1000 transactions
│   (Data Forge)      │           + Inject 3 intelligence traps
└──────────┬──────────┘
           │ transactions.csv
           ↓
┌─────────────────────┐
│   PATTERN AGENT     │  Step 3-5: LLM analyzes failure clusters
│   (The Brain)       │           + Makes profit-aware decisions
└──────────┬──────────┘           + Validates via Pydantic
           │ AgentDecision objects
           ↓
┌─────────────────────┐
│   WAR ROOM UI       │  Step 6-7: Streamlit dashboard
│   (The Story)       │           + Shows patterns discovered
└─────────────────────┘           + Displays ₹ impact
```

---

## 📋 IMPLEMENTATION ROADMAP

### Time Allocation (16 Hours Total)
- **Setup** (30 min): Environment, dependencies, config
- **Chaos Engine** (2 hrs): Data generation with intelligent traps
- **Pydantic Models** (30 min): LLM output validation
- **Pattern Agent** (6 hrs): The LLM reasoning core (MOST CRITICAL)
- **Dashboard** (4 hrs): Streamlit UI with metrics
- **Testing & Polish** (3 hrs): End-to-end validation, bug fixes

### Project Structure
```
sentinel/
├── config.py              # All constants (costs, thresholds)
├── chaos_engine.py        # Synthetic data generator
├── models.py              # Pydantic validation schemas
├── pattern_agent.py       # LLM decision engine
├── dashboard.py           # Streamlit UI
├── requirements.txt       # Dependencies
├── .env                   # API keys
├── transactions.csv       # Generated data (output)
└── README.md              # Hackathon submission
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
A synthetic transaction generator that creates 1000 payment records with 3 embedded "intelligence traps" - patterns that require AI reasoning to discover.

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
    "bank": str,                         # Enum: [HDFC, SBI, ICICI, Axis]
    "card_type": str,                    # Enum: [Debit, Credit, Rewards]
    "amount": float,                     # Range: ₹10 - ₹15,000
    "status": str,                       # Enum: [SUCCESS, FAILED]
    "latency_ms": int,                   # Normal distribution ~250ms
    "error_code": str | None             # If FAILED: [TIMEOUT, DECLINED, NETWORK_ERROR]
}
```

**Baseline behavior**:
- 92% success rate (mimics real payment systems)
- Random distribution across banks/card types
- Timestamps spread over 24-hour window

#### Component 2.2: Intelligence Trap #1 - "The Cascading Whale"
**Pattern characteristics**:
- **Trigger**: `bank == "HDFC" AND card_type == "Rewards" AND amount > 5000 AND hour IN [14, 15]`
- **Behavior**: 98% failure rate (nearly deterministic)
- **Error**: `TIMEOUT` with latency ~8000ms

**Why it's hard**:
- Requires 4-dimensional correlation (bank + card + amount + time)
- Not all HDFC fails (only Rewards)
- Not all Rewards fail (only >₹5K)
- Not all >₹5K fail (only during 14:00-16:00)

**Expected volume**: 40-60 transactions (enough to be statistically significant)

**Business impact**: High margin (₹156 avg) × High volume = ₹6,000+ savings opportunity

#### Component 2.3: Intelligence Trap #2 - "The Margin Destroyer"
**Pattern characteristics**:
- **Trigger**: `bank == "SBI" AND amount < 100`
- **Behavior**: 75% failure rate
- **Error**: `DECLINED`

**Why it's hard**:
- Pattern is obvious (simple amount filter)
- But the AI must realize it's UNPROFITABLE to fix
- Margin = ₹2 (avg), Reroute cost = ₹15 → Net: -₹13

**Expected volume**: 100-150 transactions (high noise)

**Critical insight**: The AI must recommend `IGNORE`, not `REROUTE` (tests profit awareness)

#### Component 2.4: Intelligence Trap #3 - "The Canary Spike"
**Pattern characteristics**:
- **Phase 1 (Early Warning)**: `bank == "ICICI" AND card_type == "Debit"` shows failure rate jump from 5% → 18%
- **Phase 2 (Total Outage)**: 30 minutes later, ALL ICICI transactions fail (100%)

**Why it's hard**:
- Requires temporal correlation (detecting failure rate acceleration)
- AI must predict future failures based on early warning signal
- Not just pattern detection, but predictive reasoning

**Expected behavior**:
- Phase 1: Select 20 ICICI Debit transactions in a time cluster, fail 18% of them
- Phase 2: 30-90 minutes later, fail 100% of ALL ICICI transactions

**Critical insight**: AI must recommend `ALERT` (ops intervention), not `REROUTE` (futile expense)

### CHECKPOINT 2: Validation

**What to check**:
✅ File `transactions.csv` created with exactly 1000 rows  
✅ Overall failure rate: 15-25% (realistic)  
✅ Trap 1 (HDFC Whale): 40-60 affected txns, >95% failure rate  
✅ Trap 2 (SBI Micro): 100-150 affected txns, ~75% failure rate  
✅ Trap 3 (ICICI Canary): Clear spike visible when sorted by timestamp  

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

5. **decision** (enum: "REROUTE", "IGNORE", "ALERT")
   - The final action

6. **reasoning** (string, min 100 chars)
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
For each failure cluster, analyze THREE dimensions:

1. PATTERN DETECTION
   - Is this isolated or systemic?
   - What's the specific segment? (bank + card + amount + time)
   - Example: "HDFC Rewards >₹5K failing at 2PM" = pattern
   - Example: "Random HDFC failures" = noise

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

## STEP 5: BASELINE COMPARISON (1 hour)

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
✅ Baseline system implemented  
✅ Baseline shows negative net profit  
✅ SENTINEL shows positive net profit  
✅ Delta is >₹1,500  

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

#### Component 6.6: (Optional) Live Transaction Feed
**If time permits**: Scrolling list of recent transactions with status

### CHECKPOINT 6: Validation

**What to check**:
✅ Dashboard runs: `streamlit run dashboard.py`  
✅ All metrics display correctly  
✅ 3 pattern cards visible and properly formatted  
✅ Comparison chart shows clear advantage  
✅ No errors in console  
✅ Looks professional (not cluttered)  

**AI Review Prompt**:
```
"Step 6 complete. Screenshot of dashboard:
[PASTE SCREENSHOT OR DESCRIBE LAYOUT]

Questions:
1. Is the story clear at a glance?
2. Too cluttered or too sparse?
3. Any UI improvements?"
```

---

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

## FINAL DEMO PREPARATION

### The 3-Minute Pitch Script

**Minute 1: The Problem**
```
"Traditional payment systems treat all failures equally. 
Show [Baseline metrics]: They rerouted 200 failures, 
spent ₹3,000, and LOST ₹2,200. 
That's burning capital to fix ₹10 transactions."
```

**Minute 2: The Solution**
```
"SENTINEL uses AI to find patterns humans miss.
Click [Run Analysis] → Watch it discover:
• Pattern 1: HDFC Rewards >₹5K failing at 2PM
• Pattern 2: SBI micro-transactions (unprofitable to fix)
• Pattern 3: ICICI spike (early warning of outage)

This isn't just error handling. It's pattern intelligence."
```

**Minute 3: The Impact**
```
Point to [Comparison Chart]:
SENTINEL rerouted only 47 failures (vs 200)
Spent ₹705 (vs ₹3,000)
Net profit: +₹847 (vs -₹2,200)

That's a ₹3,047 swing. And look [point to reasoning]:
Every decision has business justification.
No black boxes. Complete explainability.
```

### Pre-Demo Checklist

**24 Hours Before**:
✅ Run pipeline 10 times, verify consistency  
✅ Take screenshots of perfect run  
✅ Prepare backup (pre-generated results if LLM fails)  
✅ Write README.md with setup instructions  

**1 Hour Before**:
✅ Test on fresh Python environment  
✅ Verify API key works  
✅ Practice demo script (60 seconds, timed)  
✅ Have backup laptop  

**5 Minutes Before**:
✅ Dashboard already loaded  
✅ Terminal ready for "one command" demo  
✅ Water, charger, confidence  

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

✅ **Data Quality**: 1000 transactions, 3 clear patterns, 15-25% failure rate  
✅ **Pattern Detection**: LLM finds all 3 traps consistently (5/5 runs)  
✅ **Decision Quality**: >85% accuracy, no contradictory logic  
✅ **Explainability**: Every decision has 100+ word business reasoning  
✅ **Financial Impact**: Net profit >₹500, baseline is negative  
✅ **UI Clarity**: Non-technical person can understand dashboard in 30 seconds  
✅ **Reliability**: Runs 10 times without crash  
✅ **Demo-Readiness**: <3 minute pitch tells compelling story  

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