"""
Forex Currency Conversion Utility
Uses ExchangeRate-API (free tier, no auth required)
"""

import requests
from typing import Dict, Optional
import json
from datetime import datetime, timedelta

# Free forex API (no key required)
FOREX_API_BASE = "https://api.exchangerate-api.com/v4/latest/INR"

# Cache for forex rates (refresh every hour)
_forex_cache = {
    "rates": None,
    "timestamp": None,
    "cache_duration": 3600  # 1 hour in seconds
}


def get_forex_rates() -> Optional[Dict[str, float]]:
    """
    Fetch current forex rates with INR as base currency
    Returns dict of currency codes to INR conversion rates
    """
    # Check cache first
    if _forex_cache["rates"] and _forex_cache["timestamp"]:
        elapsed = (datetime.now() - _forex_cache["timestamp"]).total_seconds()
        if elapsed < _forex_cache["cache_duration"]:
            return _forex_cache["rates"]
    
    try:
        response = requests.get(FOREX_API_BASE, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Store in cache
        _forex_cache["rates"] = data.get("rates", {})
        _forex_cache["timestamp"] = datetime.now()
        
        return _forex_cache["rates"]
    
    except Exception as e:
        print(f"⚠️  Forex API error: {e}")
        # Return fallback static rates if API fails
        return get_fallback_rates()


def get_fallback_rates() -> Dict[str, float]:
    """Fallback static rates when API is unavailable"""
    return {
        "USD": 0.012,   # 1 INR = 0.012 USD
        "EUR": 0.011,   # 1 INR = 0.011 EUR
        "GBP": 0.0095,  # 1 INR = 0.0095 GBP
        "AED": 0.044,   # 1 INR = 0.044 AED
        "SGD": 0.016,   # 1 INR = 0.016 SGD
        "AUD": 0.019,   # 1 INR = 0.019 AUD
        "INR": 1.0
    }


def convert_to_inr(amount: float, from_currency: str) -> float:
    """
    Convert foreign currency amount to INR
    
    Args:
        amount: Amount in foreign currency
        from_currency: Currency code (USD, EUR, GBP, etc.)
    
    Returns:
        Amount in INR
    """
    if from_currency == "INR":
        return amount
    
    rates = get_forex_rates()
    if not rates or from_currency not in rates:
        # Use fallback
        rates = get_fallback_rates()
    
    # Convert: amount in foreign currency / rate = amount in INR
    # Example: 100 USD / 0.012 = 8333.33 INR
    try:
        inr_per_foreign = 1.0 / rates[from_currency]
        return round(amount * inr_per_foreign, 2)
    except (KeyError, ZeroDivisionError):
        print(f"⚠️  Currency {from_currency} not supported, using 1:83 fallback")
        return round(amount * 83, 2)  # Rough USD:INR fallback


def get_currency_symbol(currency_code: str) -> str:
    """Get currency symbol for display"""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "AED": "د.إ",
        "SGD": "S$",
        "AUD": "A$",
        "INR": "₹"
    }
    return symbols.get(currency_code, currency_code)


def format_conversion(amount: float, from_currency: str, to_inr: float) -> str:
    """Format conversion for display"""
    symbol = get_currency_symbol(from_currency)
    return f"{symbol}{amount:,.2f} → ₹{to_inr:,.2f}"


# Test function
if __name__ == "__main__":
    print("Testing Forex API...")
    rates = get_forex_rates()
    print(f"✓ Fetched {len(rates)} currency rates")
    
    # Test conversions
    test_amount = 100
    for currency in ["USD", "EUR", "GBP", "AED"]:
        inr_amount = convert_to_inr(test_amount, currency)
        print(f"  {test_amount} {currency} = ₹{inr_amount:,.2f}")
