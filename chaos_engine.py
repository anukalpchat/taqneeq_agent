"""
CHAOS ENGINE - Synthetic Transaction Data Generator
Generates 2500 realistic payment transactions with 4 embedded intelligence traps.
"""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import config

# Set random seed for reproducibility
random.seed(config.RANDOM_SEED)
np.random.seed(config.RANDOM_SEED)


def generate_transaction_id(index):
    """Generate unique transaction ID"""
    return f"TXN{index:05d}"


def generate_timestamp(index, total):
    """Generate evenly distributed timestamps over 24-hour window"""
    # Distribute transactions evenly across the time window
    seconds_elapsed = (config.DURATION_HOURS * 3600 * index) / total
    return config.START_TIME + timedelta(seconds=seconds_elapsed)


def generate_amount():
    """Generate transaction amount using lognormal distribution (realistic)"""
    # Lognormal gives us many small transactions, few large ones
    amount = np.random.lognormal(mean=np.log(config.AMOUNT_MEAN), sigma=0.8)
    # Clip to min/max range
    amount = max(config.AMOUNT_MIN, min(config.AMOUNT_MAX, amount))
    return round(amount, 2)


def generate_latency(is_failing=False, multiplier=1.0):
    """Generate latency with occasional outliers"""
    if random.random() < config.LATENCY_OUTLIER_RATE:
        # Outlier latency
        latency = random.randint(config.LATENCY_OUTLIER_THRESHOLD_MS, 5000)
    else:
        # Normal latency
        latency = int(np.random.normal(config.LATENCY_MEAN_MS, config.LATENCY_STD_MS))
        latency = max(50, latency)  # Minimum 50ms
    
    # Apply multiplier for pattern-based failures
    if is_failing:
        latency = int(latency * multiplier)
    
    return latency


def matches_pattern(txn, pattern_name):
    """Check if transaction matches a pattern's conditions"""
    pattern = config.PATTERNS[pattern_name]
    conditions = pattern["conditions"]
    
    # Check whale_trap
    if pattern_name == "whale_trap":
        return (
            txn["bank"] == conditions["bank"] and
            txn["card_type"] == conditions["card_type"] and
            txn["amount"] > conditions["amount_min"] and
            txn["timestamp"].hour in conditions["hour_range"]
        )
    
    # Check margin_destroyer
    elif pattern_name == "margin_destroyer":
        return (
            txn["bank"] == conditions["bank"] and
            txn["amount"] < conditions["amount_max"]
        )
    
    # Check canary_spike (Phase 1 or Phase 2)
    elif pattern_name == "canary_spike":
        hour = txn["timestamp"].hour
        minute = txn["timestamp"].minute
        
        phase1 = pattern["phase_1"]
        phase2 = pattern["phase_2"]
        
        # Phase 1: 18:00-18:30
        in_phase1 = (hour == phase1["start_hour"] and minute < phase1["duration_minutes"])
        
        # Phase 2: 19:00-20:00
        in_phase2 = (hour >= phase2["start_hour"] and hour < phase2["start_hour"] + 1)
        
        return (
            txn["bank"] == conditions["bank"] and
            txn["card_type"] == conditions["card_type"] and
            (in_phase1 or in_phase2)
        )
    
    # Check weekend_vip
    elif pattern_name == "weekend_vip":
        # Check if it's a weekend (Saturday=5, Sunday=6)
        is_weekend = txn["timestamp"].weekday() >= 5
        
        return (
            txn["customer_tier"] == conditions["customer_tier"] and
            txn["merchant_category"] == conditions["merchant_category"] and
            is_weekend
        )
    
    return False


def should_fail_for_pattern(txn, pattern_name):
    """Determine if transaction should fail based on pattern logic"""
    pattern = config.PATTERNS[pattern_name]
    
    if pattern_name == "canary_spike":
        # Special handling for two-phase pattern
        hour = txn["timestamp"].hour
        minute = txn["timestamp"].minute
        
        phase1 = pattern["phase_1"]
        phase2 = pattern["phase_2"]
        
        # Phase 1: 18% failure rate
        if hour == phase1["start_hour"] and minute < phase1["duration_minutes"]:
            return random.random() < phase1["failure_rate"]
        
        # Phase 2: 100% failure rate
        if hour >= phase2["start_hour"]:
            return random.random() < phase2["failure_rate"]
        
        return False
    
    else:
        # Standard failure rate check
        return random.random() < pattern["failure_rate"]


def get_error_code_for_pattern(pattern_name, txn):
    """Get error code for a pattern-matched failure"""
    pattern = config.PATTERNS[pattern_name]
    
    # Handle canary_spike phases
    if pattern_name == "canary_spike":
        hour = txn["timestamp"].hour
        phase1 = pattern["phase_1"]
        phase2 = pattern["phase_2"]
        
        if hour == phase1["start_hour"]:
            return phase1["error_code"]
        else:
            return phase2["error_code"]
    
    # Check if we should inject diversity (noise)
    if random.random() < pattern.get("error_diversity", 0):
        # Return random error code for noise
        return random.choice(config.ALL_ERROR_CODES)
    
    # Return primary error code for this pattern
    return pattern["error_code"]


def generate_base_transaction(index, forced_attributes=None):
    """Generate a single base transaction with random or forced attributes"""
    timestamp = generate_timestamp(index, config.TOTAL_TRANSACTIONS)
    
    # Determine if international transaction
    is_international = random.random() < config.INTERNATIONAL_RATE
    currency = "INR"
    original_amount = generate_amount()
    
    if is_international:
        # Select currency based on weights
        currency = random.choices(
            config.INTERNATIONAL_CURRENCIES,
            weights=config.INTERNATIONAL_CURRENCY_WEIGHTS,
            k=1
        )[0]
        # Convert amount to foreign currency (rough approximation)
        if currency == "USD":
            original_amount = round(original_amount * 0.012, 2)
        elif currency == "EUR":
            original_amount = round(original_amount * 0.011, 2)
        elif currency == "GBP":
            original_amount = round(original_amount * 0.0095, 2)
        elif currency == "AED":
            original_amount = round(original_amount * 0.044, 2)
        elif currency == "SGD":
            original_amount = round(original_amount * 0.016, 2)
        elif currency == "AUD":
            original_amount = round(original_amount * 0.019, 2)
    
    txn = {
        "transaction_id": generate_transaction_id(index),
        "timestamp": timestamp,
        "bank": random.choice(config.BANKS),
        "card_type": random.choice(config.CARD_TYPES),
        "merchant_category": random.choice(config.MERCHANT_CATEGORIES),
        "customer_tier": random.choice(config.CUSTOMER_TIERS),
        "amount": original_amount,
        "currency": currency,
        "is_international": is_international,
        "status": "SUCCESS",  # Default, will be overridden if fails
        "latency_ms": generate_latency(),
        "error_code": None
    }
    
    # Override with forced attributes if provided
    if forced_attributes:
        txn.update(forced_attributes)
    
    return txn


def inject_pattern_failures(transactions):
    """Inject intelligence trap patterns into transactions"""
    pattern_stats = {name: {"matched": 0, "failed": 0} for name in config.PATTERNS.keys()}
    
    for txn in transactions:
        # Check each pattern in priority order
        for pattern_name in ["whale_trap", "margin_destroyer", "canary_spike", "weekend_vip"]:
            if matches_pattern(txn, pattern_name):
                pattern_stats[pattern_name]["matched"] += 1
                
                # Determine if this should fail
                if should_fail_for_pattern(txn, pattern_name):
                    pattern_stats[pattern_name]["failed"] += 1
                    txn["status"] = "FAILED"
                    txn["error_code"] = get_error_code_for_pattern(pattern_name, txn)
                    
                    # Apply latency multiplier
                    multiplier = config.PATTERNS[pattern_name].get("latency_multiplier", 1.0)
                    txn["latency_ms"] = generate_latency(is_failing=True, multiplier=multiplier)
                
                # Only match first pattern (no overlapping patterns)
                break
    
    return pattern_stats


def inject_random_failures(transactions):
    """Add random noise failures (70% of total failures should be random)"""
    random_failures = 0
    
    for txn in transactions:
        # Skip if already failed due to pattern
        if txn["status"] == "FAILED":
            continue
        
        # Apply baseline failure rate to non-pattern transactions
        if random.random() > config.BASE_SUCCESS_RATE:
            txn["status"] = "FAILED"
            txn["error_code"] = random.choice(config.ALL_ERROR_CODES)
            txn["latency_ms"] = generate_latency(is_failing=True, multiplier=1.5)
            random_failures += 1
    
    return random_failures


def calculate_statistics(transactions):
    """Calculate and display generation statistics"""
    df = pd.DataFrame(transactions)
    
    total = len(df)
    successes = len(df[df["status"] == "SUCCESS"])
    failures = len(df[df["status"] == "FAILED"])
    success_rate = successes / total
    
    print(f"\n{'='*60}")
    print(f"CHAOS ENGINE - DATA GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total Transactions: {total}")
    print(f"Successes: {successes} ({success_rate:.1%})")
    print(f"Failures: {failures} ({1-success_rate:.1%})")
    print(f"\nAmount Range: ₹{df['amount'].min():.2f} - ₹{df['amount'].max():.2f}")
    print(f"Average Amount: ₹{df['amount'].mean():.2f}")
    print(f"Average Latency: {df['latency_ms'].mean():.0f}ms")
    
    return {
        "total_transactions": total,
        "successes": successes,
        "failures": failures,
        "success_rate": success_rate
    }


def save_ground_truth(pattern_stats, overall_stats):
    """Save ground truth data for validation"""
    ground_truth = {
        "generation_timestamp": datetime.now().isoformat(),
        "configuration": {
            "total_transactions": config.TOTAL_TRANSACTIONS,
            "base_success_rate": config.BASE_SUCCESS_RATE,
            "random_seed": config.RANDOM_SEED
        },
        "patterns_injected": {},
        "overall_statistics": overall_stats,
        "expected_outcomes": {
            "whale_trap": {
                "action": "REROUTE",
                "reasoning": "High-value transactions with good margin, profitable to fix"
            },
            "margin_destroyer": {
                "action": "IGNORE",
                "reasoning": "Low-value transactions, reroute cost exceeds margin (unprofitable)"
            },
            "canary_spike": {
                "action": "ALERT",
                "reasoning": "Escalating failure pattern indicates infrastructure issue, alert ops team"
            },
            "weekend_vip": {
                "action": "REROUTE",
                "reasoning": "Medium-high value VIP customers, profitable and retention-critical"
            }
        }
    }
    
    # Add pattern statistics
    for pattern_name, stats in pattern_stats.items():
        ground_truth["patterns_injected"][pattern_name] = {
            "description": config.PATTERNS[pattern_name]["description"],
            "matched_transactions": stats["matched"],
            "failed_transactions": stats["failed"],
            "failure_rate": stats["failed"] / stats["matched"] if stats["matched"] > 0 else 0,
            "expected_action": config.PATTERNS[pattern_name]["expected_action"],
            "profitability": config.PATTERNS[pattern_name]["profitability"]
        }
    
    # Ensure directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Save to JSON
    with open(config.GROUND_TRUTH, 'w') as f:
        json.dump(ground_truth, f, indent=2)
    
    print(f"\nGround truth saved to: {config.GROUND_TRUTH}")


def force_inject_pattern_transactions(transactions):
    """Force-inject transactions matching pattern criteria to guarantee volumes"""
    print("\nForce-injecting pattern transactions to guarantee volumes...")
    
    injection_count = 0
    available_indices = list(range(len(transactions)))
    random.shuffle(available_indices)
    
    # Pattern 1: Whale Trap - HDFC Rewards >₹5K at 14:00-16:00
    whale_target = config.PATTERNS["whale_trap"]["target_volume"]
    print(f"  Injecting {whale_target} whale_trap transactions...")
    for i in range(whale_target):
        if not available_indices:
            break
        idx = available_indices.pop()
        
        # Create timestamp in 14:00-16:00 window
        hour = random.choice([14, 15])
        minute = random.randint(0, 59)
        timestamp = config.START_TIME.replace(hour=hour, minute=minute)
        
        transactions[idx] = generate_base_transaction(idx, forced_attributes={
            "timestamp": timestamp,
            "bank": "HDFC",
            "card_type": "Rewards",
            "amount": round(random.uniform(5500, 12000), 2)  # Ensure >5K
        })
        injection_count += 1
    
    # Pattern 2: Margin Destroyer - SBI <₹100
    margin_target = config.PATTERNS["margin_destroyer"]["target_volume"]
    print(f"  Injecting {margin_target} margin_destroyer transactions...")
    for i in range(margin_target):
        if not available_indices:
            break
        idx = available_indices.pop()
        
        transactions[idx] = generate_base_transaction(idx, forced_attributes={
            "bank": "SBI",
            "amount": round(random.uniform(10, 99), 2)  # Ensure <100
        })
        injection_count += 1
    
    # Pattern 3: Canary Spike - ICICI Debit at 18:00-19:00
    canary_target = config.PATTERNS["canary_spike"]["target_volume"]
    print(f"  Injecting {canary_target} canary_spike transactions...")
    
    # Split between phase 1 (18:00-18:30) and phase 2 (19:00-20:00)
    phase1_count = canary_target // 3  # 1/3 in phase 1
    phase2_count = canary_target - phase1_count  # 2/3 in phase 2
    
    # Phase 1 transactions
    for i in range(phase1_count):
        if not available_indices:
            break
        idx = available_indices.pop()
        
        minute = random.randint(0, 29)  # 18:00-18:29
        timestamp = config.START_TIME.replace(hour=18, minute=minute)
        
        transactions[idx] = generate_base_transaction(idx, forced_attributes={
            "timestamp": timestamp,
            "bank": "ICICI",
            "card_type": "Debit"
        })
        injection_count += 1
    
    # Phase 2 transactions
    for i in range(phase2_count):
        if not available_indices:
            break
        idx = available_indices.pop()
        
        hour = 19
        minute = random.randint(0, 59)
        timestamp = config.START_TIME.replace(hour=hour, minute=minute)
        
        transactions[idx] = generate_base_transaction(idx, forced_attributes={
            "timestamp": timestamp,
            "bank": "ICICI",
            "card_type": "Debit"
        })
        injection_count += 1
    
    # Pattern 4: Weekend VIP - Already has 200 matches, skip forcing (it's over-represented naturally)
    # Just let random generation handle this one
    
    print(f"  Total forced injections: {injection_count}")
    return injection_count


def main():
    """Main execution function"""
    print("Starting CHAOS ENGINE...")
    print(f"Generating {config.TOTAL_TRANSACTIONS} transactions with 4 intelligence traps\n")
    
    # Generate base transactions
    print("Step 1: Generating base transactions...")
    transactions = [generate_base_transaction(i) for i in range(config.TOTAL_TRANSACTIONS)]
    
    # Force-inject pattern transactions
    print("Step 2: Force-injecting pattern transactions...")
    force_inject_pattern_transactions(transactions)
    
    # Inject pattern failures
    print("\nStep 3: Applying failure logic to patterns...")
    pattern_stats = inject_pattern_failures(transactions)
    
    # Print pattern injection results
    print("\nPattern Injection Results:")
    for pattern_name, stats in pattern_stats.items():
        print(f"  {pattern_name:20s}: {stats['matched']:3d} matched, {stats['failed']:3d} failed")
    
    # Inject random failures
    print("\nStep 4: Adding random noise failures...")
    random_failures = inject_random_failures(transactions)
    print(f"  Random failures added: {random_failures}")
    
    # Calculate statistics
    overall_stats = calculate_statistics(transactions)
    
    # Save to CSV
    print(f"\nStep 5: Saving data...")
    df = pd.DataFrame(transactions)
    
    # Ensure directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Save CSV
    df.to_csv(config.OUTPUT_CSV, index=False)
    print(f"  CSV saved to: {config.OUTPUT_CSV}")
    
    # Save JSON
    df.to_json(config.OUTPUT_JSON, orient='records', date_format='iso', indent=2)
    print(f"  JSON saved to: {config.OUTPUT_JSON}")
    
    # Save ground truth
    save_ground_truth(pattern_stats, overall_stats)
    
    print(f"\n{'='*60}")
    print("SUCCESS! Data generation complete.")
    print("Ready for pattern analysis.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
