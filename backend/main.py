from groq_api import extract_parameters_from_user_input, summarize_hotels
from booking_api import get_hotels
from utils import ensure_dates_not_past, extract_parameters
import json
def main():
    user_input = input("✈️ Tell me about your dream trip: ")

    try:
        params = extract_parameters(user_input)
        params = ensure_dates_not_past(params)
    except Exception as e:
        print(f"Error parsing input: {e}")
        return

    print(f"\n🔎 Searching hotels for: {params.get('location')}")
    print(f"📅 Dates: {params.get('arrival_date')} to {params.get('departure_date')}\n")

    try:
        hotel_data = get_hotels(params)
    except Exception as e:
        print(f"Error fetching hotels: {e}")
        return

    # Extract hotel list from common keys
    hotels_list = hotel_data.get('result', [])

    if hotels_list:
        print("Example hotel data (first hotel):")
        print(json.dumps(hotels_list[0], indent=2))
    else:
        print("No hotels found.")


    if not hotels_list:
        print("No hotels found for your criteria.")
        return

    try:
        summary = summarize_hotels(hotel_data, filters=params, user_input=user_input)
    except Exception as e:
        print(f"Error summarizing hotels: {e}")
        return

    print("\n📋 Summary of your hotel options:\n")
    print(summary)

if __name__ == "__main__":
    main()
