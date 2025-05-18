from booking_api import get_hotels
from flight_agent import FlightAgent
from groq_api import extract_parameters_from_user_input, summarize_hotels
from utils import ensure_dates_not_past
import json
import argparse
import re

def determine_query_type(user_input):
    """Determine if the query is about flights, hotels, or both."""
    user_input = user_input.lower()
    
    # Check for flight-related keywords
    flight_keywords = ["flight", "fly", "plane", "airline", "airport", "departure", "arrival"]
    hotel_keywords = ["hotel", "stay", "accommodation", "room", "lodge", "resort", "book a room"]
    
    flight_score = sum(1 for keyword in flight_keywords if keyword in user_input)
    hotel_score = sum(1 for keyword in hotel_keywords if keyword in user_input)
    
    # If both flight and hotel keywords are present, assume it's a trip (both)
    if flight_score > 0 and hotel_score > 0:
        return "trip"
    elif flight_score > hotel_score:
        return "flight"
    else:
        return "hotel"  # Default to hotel if can't determine

def main():
    parser = argparse.ArgumentParser(description="Travel Assistant - Find flights and hotels")
    parser.add_argument("--type", choices=["flight", "hotel", "trip", "auto"], default="auto",
                        help="Specify search type (flight, hotel, trip, or auto-detect)")
    args, remaining = parser.parse_known_args()
    
    # Get user input either from command line args or interactively
    if remaining:
        user_input = " ".join(remaining)
    else:
        user_input = input("✈️ Tell me about your travel plans: ")
    
    # Determine what type of search to perform
    query_type = args.type
    if query_type == "auto":
        query_type = determine_query_type(user_input)
        print(f"\n🔍 Query detected as: {query_type.upper()}")
    
    # Perform search based on type
    if query_type in ["hotel", "trip"]:
        # Hotel search
        try:
            hotel_params = extract_parameters_from_user_input(user_input)
            hotel_params = ensure_dates_not_past(hotel_params)
            print(f"\n🏨 Searching hotels for: {hotel_params.get('location')}")
            print(f"📅 Dates: {hotel_params.get('arrival_date')} to {hotel_params.get('departure_date')}")
            
            hotel_data = get_hotels(hotel_params)
            hotel_summary = summarize_hotels(hotel_data, hotel_params, user_input)
            print("\n📋 Hotel Options:\n")
            print(hotel_summary)
        except Exception as e:
            print(f"Error with hotel search: {e}")
    
    if query_type in ["flight", "trip"]:
        # Flight search
        try:
            flight_agent = FlightAgent()
            flight_results = flight_agent.get_flight_recommendations(user_input)
            
            print("\n✈️ Flight Options:\n")
            print(flight_results["summary"])
        except Exception as e:
            print(f"Error with flight search: {e}")

    print("\n✅ Search complete! Thanks for using our Travel Assistant.")

if __name__ == "__main__":
    main()
