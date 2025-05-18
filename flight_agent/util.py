import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_parameters(user_input):
    """
    Import and use Groq API's extract_parameters_from_user_input function.
    This is a thin wrapper to maintain backward compatibility.
    """
    from groq_api import extract_parameters_from_user_input
    return extract_parameters_from_user_input(user_input)

def ensure_dates_not_past(params):
    """
    Ensure that arrival and departure dates are not in the past.
    If they are, adjust them to reasonable future dates.
    
    Args:
        params (dict): Dictionary containing arrival_date and departure_date keys
        
    Returns:
        dict: Updated parameters dictionary with valid future dates
    """
    today = datetime.today().date()
    
    # Handle missing dates by setting defaults
    if "arrival_date" not in params or not params["arrival_date"]:
        # Default arrival: 1 month from today
        next_month = today + timedelta(days=30)
        params["arrival_date"] = next_month.isoformat()
    
    if "departure_date" not in params or not params["departure_date"]:
        # Default departure: 3 days after arrival
        arrival = datetime.fromisoformat(params["arrival_date"]).date()
        params["departure_date"] = (arrival + timedelta(days=3)).isoformat()
    
    # Parse dates
    try:
        arrival = datetime.strptime(params["arrival_date"], "%Y-%m-%d").date()
        departure = datetime.strptime(params["departure_date"], "%Y-%m-%d").date()
    except ValueError:
        # If date parsing fails, set default dates
        next_month = today + timedelta(days=30)
        arrival = next_month
        departure = next_month + timedelta(days=3)
        params["arrival_date"] = arrival.isoformat()
        params["departure_date"] = departure.isoformat()
        return params
    
    # Ensure arrival is not in the past
    if arrival < today:
        arrival = today + timedelta(days=1)  # Set to tomorrow
        params["arrival_date"] = arrival.isoformat()
    
    # Ensure departure is after arrival
    if departure <= arrival:
        # Set departure to 3 days after arrival or at least 1 day after
        departure = arrival + timedelta(days=max(3, 1))
        params["departure_date"] = departure.isoformat()
    
    return params

def format_currency(amount, currency="USD"):
    """Format a number as currency."""
    if amount is None:
        return "Price unavailable"
    
    try:
        amount = float(amount)
        if currency == "USD":
            return f"${amount:.2f}"
        else:
            return f"{amount:.2f} {currency}"
    except (ValueError, TypeError):
        return str(amount)

def validate_api_keys():
    """Check if all required API keys are present in environment variables."""
    required_keys = ["RAPIDAPI_KEY", "GROQ_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print("Warning: The following required API keys are missing:")
        for key in missing_keys:
            print(f"  - {key}")
        return False
    return True

if __name__ == "__main__":
    # Test the date adjustment function
    test_params = {
        "location": "San Francisco",
        "arrival_date": "2020-01-01",  # Past date
        "departure_date": "2020-01-05"  # Past date
    }
    
    updated = ensure_dates_not_past(test_params)
    print("Original:", test_params)
    print("Updated:", updated)
