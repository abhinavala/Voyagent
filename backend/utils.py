from datetime import datetime
from groq_api import extract_parameters_from_user_input

def extract_parameters(user_input):
    return extract_parameters_from_user_input(user_input)

def ensure_dates_not_past(params):
    today = datetime.today().date()
    arrival = datetime.strptime(params["arrival_date"], "%Y-%m-%d").date()
    departure = datetime.strptime(params["departure_date"], "%Y-%m-%d").date()

    if arrival < today:
        arrival = today
        # Default stay of 3 days or till day 28 of current month, whichever is less
        new_departure_day = min(today.day + 3, 28)
        # Safely replace day, handling month length
        try:
            departure = today.replace(day=new_departure_day)
        except ValueError:
            # If day invalid (e.g. 31 in shorter month), set departure to last day of month
            departure = today

        params["arrival_date"] = arrival.isoformat()
        params["departure_date"] = departure.isoformat()

    return params
