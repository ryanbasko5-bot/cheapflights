"""
Currency converter based on phone number country code
"""
import requests
from typing import Dict

# Phone code to currency mapping
PHONE_CODE_TO_CURRENCY = {
    '+1': 'USD',      # US/Canada
    '+44': 'GBP',     # UK
    '+61': 'AUD',     # Australia
    '+64': 'NZD',     # New Zealand
    '+65': 'SGD',     # Singapore
    '+81': 'JPY',     # Japan
    '+82': 'KRW',     # South Korea
    '+86': 'CNY',     # China
    '+91': 'INR',     # India
    '+33': 'EUR',     # France
    '+49': 'EUR',     # Germany
    '+39': 'EUR',     # Italy
    '+34': 'EUR',     # Spain
    '+66': 'THB',     # Thailand
    '+63': 'PHP',     # Philippines
    '+60': 'MYR',     # Malaysia
    '+62': 'IDR',     # Indonesia
    '+84': 'VND',     # Vietnam
    '+852': 'HKD',    # Hong Kong
    '+886': 'TWD',    # Taiwan
}

def get_currency_from_phone(phone_number: str) -> str:
    """
    Detect currency from phone number country code
    
    Args:
        phone_number: Phone number with country code (e.g., '+61412345678')
    
    Returns:
        Currency code (e.g., 'AUD')
    """
    # Try exact matches first (e.g., +852 for Hong Kong)
    for code in ['+852', '+886', '+886']:
        if phone_number.startswith(code):
            return PHONE_CODE_TO_CURRENCY[code]
    
    # Try two-digit codes
    for code in ['+91', '+86', '+84', '+82', '+81', '+66', '+65', '+64', '+63', '+62', '+60', '+49', '+44', '+39', '+34', '+33', '+61']:
        if phone_number.startswith(code):
            return PHONE_CODE_TO_CURRENCY[code]
    
    # Try single-digit code (+1)
    if phone_number.startswith('+1'):
        return PHONE_CODE_TO_CURRENCY['+1']
    
    # Default to USD
    return 'USD'


def convert_currency(amount: float, from_currency: str, to_currency: str) -> Dict:
    """
    Convert currency using free exchange rate API
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., 'EUR')
        to_currency: Target currency code (e.g., 'AUD')
    
    Returns:
        Dict with converted amount and rate
    """
    if from_currency == to_currency:
        return {
            'amount': amount,
            'currency': to_currency,
            'rate': 1.0,
            'original_amount': amount,
            'original_currency': from_currency
        }
    
    try:
        # Use free exchangerate-api.com (no API key needed for basic use)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(to_currency)
            
            if rate:
                converted = amount * rate
                return {
                    'amount': round(converted, 2),
                    'currency': to_currency,
                    'rate': rate,
                    'original_amount': amount,
                    'original_currency': from_currency
                }
    
    except Exception as e:
        print(f"Currency conversion error: {e}")
    
    # Fallback: return original
    return {
        'amount': amount,
        'currency': from_currency,
        'rate': 1.0,
        'original_amount': amount,
        'original_currency': from_currency
    }


def format_price_for_sms(amount: float, currency: str) -> str:
    """
    Format price for SMS display
    
    Args:
        amount: Price amount
        currency: Currency code
    
    Returns:
        Formatted string (e.g., '$1,234' or '¥123,456')
    """
    # Currency symbols
    symbols = {
        'USD': '$', 'AUD': '$', 'CAD': '$', 'NZD': '$', 'SGD': '$', 'HKD': '$',
        'GBP': '£', 'EUR': '€', 'JPY': '¥', 'CNY': '¥', 'KRW': '₩',
        'INR': '₹', 'THB': '฿', 'PHP': '₱', 'MYR': 'RM', 'IDR': 'Rp',
        'VND': '₫', 'TWD': 'NT$'
    }
    
    symbol = symbols.get(currency, currency + ' ')
    
    # Format with commas for readability
    if amount >= 1000:
        formatted = f"{symbol}{int(amount):,}"
    else:
        formatted = f"{symbol}{int(amount)}"
    
    return formatted


# Quick test
if __name__ == "__main__":
    # Test phone number detection
    test_phones = [
        '+61412345678',  # Australia
        '+14155551234',  # US
        '+447700900123', # UK
        '+85298765432',  # Hong Kong
    ]
    
    print("🌍 Currency Detection Test:\n")
    for phone in test_phones:
        currency = get_currency_from_phone(phone)
        print(f"{phone} → {currency}")
    
    # Test conversion
    print("\n💱 Currency Conversion Test:\n")
    result = convert_currency(202.57, 'EUR', 'AUD')
    print(f"EUR €202.57 → AUD ${result['amount']}")
    print(f"Exchange rate: {result['rate']}")
    
    # Test formatting
    print("\n💰 Price Formatting Test:\n")
    prices = [
        (1234.56, 'AUD'),
        (202.57, 'EUR'),
        (50000, 'JPY'),
        (123456, 'KRW'),
    ]
    
    for amount, currency in prices:
        formatted = format_price_for_sms(amount, currency)
        print(f"{amount} {currency} → {formatted}")
