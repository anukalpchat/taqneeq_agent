"""
SENTINEL Configuration
Single source of truth for all constants, business rules, and system parameters.
"""

from datetime import datetime, timedelta

# ============================================================================
# BUSINESS CONSTANTS
# ============================================================================

# Financial Rules
REROUTE_COST = 15.00                    # Cost to reroute a transaction (₹)
MARGIN_RATE = 0.02                      # 2% merchant margin on successful transactions
VIP_THRESHOLD = 5000                    # ₹5K+ considered high-value

# Decision Thresholds
MIN_PATTERN_SIZE = 10                   # Minimum instances to consider a pattern significant
SPIKE_MULTIPLIER = 3.0                  # Failure rate must increase 3x to be a "spike"
CONFIDENCE_THRESHOLD = 0.70             # Only execute actions if confidence >= 70%

# ============================================================================
# DATA GENERATION SETTINGS
# ============================================================================

# Volume & Time
RANDOM_SEED = 42                        # For reproducible results
TOTAL_TRANSACTIONS = 2500               # Total transactions to generate
BASE_SUCCESS_RATE = 0.92                # 92% baseline success rate
START_TIME = datetime(2026, 1, 31, 0, 0, 0)
DURATION_HOURS = 24

# Transaction Dimensions
BANKS = ["HDFC", "SBI", "ICICI", "Axis", "Kotak"]
CARD_TYPES = ["Debit", "Credit", "Rewards", "Corporate"]
MERCHANT_CATEGORIES = ["E-commerce", "Travel", "Food", "Utilities"]
CUSTOMER_TIERS = ["VIP", "Regular", "New"]

# Amount Distribution (Lognormal - realistic payment distribution)
AMOUNT_MIN = 10
AMOUNT_MAX = 15000
AMOUNT_MEAN = 850                       # Geometric mean
AMOUNT_STD = 2000                       # Standard deviation

# Latency Distribution (Normal)
LATENCY_MEAN_MS = 250
LATENCY_STD_MS = 100
LATENCY_OUTLIER_THRESHOLD_MS = 2000
LATENCY_OUTLIER_RATE = 0.05

# ============================================================================
# ERROR CODE TAXONOMY
# ============================================================================

ERROR_CODES = {
    "infrastructure": [
        "TIMEOUT",
        "GATEWAY_TIMEOUT", 
        "SERVICE_UNAVAILABLE",
        "SLOW_RESPONSE"
    ],
    "policy": [
        "RISK_THRESHOLD_EXCEEDED",
        "DAILY_LIMIT_REACHED"
    ],
    "customer": [
        "INSUFFICIENT_FUNDS",
        "CARD_BLOCKED",
        "EXPIRED_CARD",
        "DECLINED"
    ],
    "fraud": [
        "SUSPICIOUS_ACTIVITY",
        "FRAUD_CHECK_TIMEOUT"
    ]
}

# Flatten for random selection
ALL_ERROR_CODES = [code for codes in ERROR_CODES.values() for code in codes]

# ============================================================================
# INTELLIGENCE TRAP PATTERNS (The 4 Patterns to Inject)
# ============================================================================

PATTERNS = {
    "whale_trap": {
        "description": "HDFC Rewards >₹5K failing during afternoon window",
        "conditions": {
            "bank": "HDFC",
            "card_type": "Rewards",
            "amount_min": 5000,
            "hour_range": [14, 15]  # 2:00 PM - 3:59 PM
        },
        "failure_rate": 0.98,
        "target_volume": 35,            # Expected matching transactions
        "error_code": "RISK_THRESHOLD_EXCEEDED",
        "error_diversity": 0.10,        # 10% use other error codes (noise)
        "latency_multiplier": 3.0,      # 3x normal latency when failing
        "expected_action": "REROUTE",
        "profitability": "HIGH"
    },
    
    "margin_destroyer": {
        "description": "SBI micro-transactions <₹100 with high failure rate",
        "conditions": {
            "bank": "SBI",
            "amount_max": 100
        },
        "failure_rate": 0.75,
        "target_volume": 85,
        "error_code": "DECLINED",
        "error_diversity": 0.20,
        "latency_multiplier": 1.0,
        "expected_action": "IGNORE",    # Unprofitable to fix
        "profitability": "NEGATIVE"
    },
    
    "canary_spike": {
        "description": "ICICI Debit escalating failure pattern",
        "conditions": {
            "bank": "ICICI",
            "card_type": "Debit"
        },
        "phase_1": {
            "start_hour": 18,           # 6:00 PM
            "duration_minutes": 30,
            "failure_rate": 0.18,       # 18% failure rate (up from 5% baseline)
            "error_code": "SLOW_RESPONSE"
        },
        "phase_2": {
            "start_hour": 19,           # 7:00 PM
            "duration_minutes": 60,
            "failure_rate": 1.00,       # 100% failure (total outage)
            "error_code": "SERVICE_UNAVAILABLE"
        },
        "target_volume": 60,
        "expected_action": "ALERT",
        "profitability": "N/A"          # Not about profit, about preventing waste
    },
    
    "weekend_vip": {
        "description": "VIP Travel transactions failing on weekends",
        "conditions": {
            "customer_tier": "VIP",
            "merchant_category": "Travel",
            "day_type": "Weekend"       # Saturday or Sunday
        },
        "failure_rate": 0.65,
        "target_volume": 22,
        "error_code": "FRAUD_CHECK_TIMEOUT",
        "error_diversity": 0.30,
        "latency_multiplier": 2.5,
        "expected_action": "REROUTE",
        "profitability": "MEDIUM"
    }
}

# ============================================================================
# LLM CONFIGURATION
# ============================================================================

LLM_MODEL = "gemini-1.5-flash"          # Gemini 1.5 Flash (fallback with separate quota)
LLM_TEMPERATURE = 0.1                   # Low temperature for deterministic reasoning
MAX_OUTPUT_TOKENS = 2000                # Maximum tokens for LLM response
LLM_TIMEOUT_SECONDS = 30
MAX_RETRIES = 2

# ============================================================================
# EMAIL ALERT SETTINGS
# ============================================================================

# SMTP Configuration (for Gmail - adjust for other providers)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True

# Email Addresses (override in .env for security)
ALERT_EMAIL_FROM = "sentinel-agent@demo.com"
ALERT_EMAIL_TO = "ops-team@demo.com"        # Can be comma-separated list

# Alert Severity Levels
ALERT_SEVERITY = {
    "LOW": "⚠️",
    "MEDIUM": "⚡",
    "HIGH": "🚨",
    "CRITICAL": "🔥"
}

# ============================================================================
# FILE PATHS & DIRECTORIES
# ============================================================================

# Directories
DATA_DIR = "data"
LOGS_DIR = "logs"

# Output Files
OUTPUT_CSV = f"{DATA_DIR}/transactions.csv"
OUTPUT_JSON = f"{DATA_DIR}/transactions.json"
GROUND_TRUTH = f"{DATA_DIR}/ground_truth.json"

# Execution Logs
EXECUTION_LOG = f"{LOGS_DIR}/execution_log.json"
EMAIL_LOG = f"{LOGS_DIR}/email_log.json"
DECISION_DB = f"{LOGS_DIR}/decisions.json"
ROUTING_CONFIG = f"{LOGS_DIR}/routing_config.json"

# ============================================================================
# DASHBOARD SETTINGS
# ============================================================================

DASHBOARD_TITLE = "SENTINEL - Pattern-Aware Payment Remediation"
DASHBOARD_SUBTITLE = "The AI That Knows When NOT To Fix Things"

# Refresh rate for live demo (seconds)
DASHBOARD_REFRESH_RATE = 2

# Chart colors
COLOR_SUCCESS = "#28a745"
COLOR_FAILURE = "#dc3545"
COLOR_REROUTE = "#007bff"
COLOR_IGNORE = "#6c757d"
COLOR_ALERT = "#ffc107"

# ============================================================================
# VALIDATION RULES
# ============================================================================

# Data Quality Checks
MIN_PATTERN_INSTANCES = 15              # Each pattern should have at least 15 instances
MAX_PATTERN_CORRELATION = 0.95          # Patterns shouldn't be 100% deterministic
BASELINE_TOLERANCE = 0.03               # 92% ±3% success rate acceptable
REQUIRE_TIMESTAMP_SPREAD = True         # Timestamps should be evenly distributed

# ============================================================================
# DEMO OPTIMIZATION
# ============================================================================

# Story arc settings
FRONT_LOAD_PATTERNS = False             # Don't make patterns obvious in first 100 transactions
DRAMATIC_TIMING = True                  # Space pattern discoveries for better narrative
INCLUDE_FALSE_ALARM = True              # Include one unprofitable pattern to test IGNORE logic

# Playback speed for simulated real-time
PLAYBACK_SPEED_MULTIPLIER = 10          # Process 10 transactions per second in demo

# ============================================================================
# ENVIRONMENT VARIABLE NAMES
# ============================================================================

ENV_OPENAI_API_KEY = "OPENAI_API_KEY"
ENV_SMTP_PASSWORD = "SMTP_PASSWORD"
ENV_ALERT_EMAIL_TO = "ALERT_EMAIL_TO"   # Override default ops email

# ============================================================================
# BASELINE COMPARISON (For Demo Metrics)
# ============================================================================

# What a "dumb" system would do (reroute everything)
BASELINE_REROUTE_ALL = True
BASELINE_EXPECTED_LOSS = -2250          # Expected net loss from baseline approach
SENTINEL_TARGET_PROFIT = 800            # Our target net profit
IMPROVEMENT_TARGET_PERCENT = 300        # 300% improvement over baseline
