import requests
import os
import re
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('flight_agent')

# Load environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

class FlightAgent:
    def __init__(self):
        self.api_key = RAPIDAPI_KEY
        if not self.api_key:
            logger.warning("RAPIDAPI_KEY is not set. API calls will fail.")
        
    def extract_flight_details(self, user_query):
        """Extract flight details from user query including locations, dates, and passenger count."""
        # Extract origin (default to empty, will need to be provided later if not found)
        origin_match = re.search(r'from\s+([A-Za-z\s,]+?)(?:\s+to|\s+on|\s+from|\s+between|\s+starting|\s+for|\s+\d|$)', user_query)
        origin = origin_match.group(1).strip() if origin_match else ""
        
        # Extract destination
        destination_match = re.search(r'to\s+([A-Za-z\s,]+?)(?:\s+from|\s+on|\s+between|\s+starting|\s+for|\s+\d|$)', user_query)
        destination = destination_match.group(1).strip() if destination_match else ""
        
        # Extract dates (departure and return)
        date_pattern = r'(?:from|between|on)\s+(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?|\d{1,2}/\d{1,2}(?:/\d{2,4})?|\d{4}-\d{2}-\d{2})'
        dates = re.findall(date_pattern, user_query, re.IGNORECASE)
        
        # More specific pattern for "Month Day to Month Day" format
        range_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?\s+to\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?'
        date_range = re.search(range_pattern, user_query, re.IGNORECASE)
        
        # Extract date range with format "July 10th to July 13th"
        date_range_pattern = r'([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s+to\s+([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?'
        date_range_match = re.search(date_range_pattern, user_query, re.IGNORECASE)
        
        depart_date = None
        return_date = None
        
        if date_range_match:
            # Get current year
            current_year = datetime.now().year
            
            # Parse departure date
            depart_month = date_range_match.group(1)
            depart_day = int(date_range_match.group(2))
            
            # Parse return date
            return_month = date_range_match.group(3)
            return_day = int(date_range_match.group(4))
            
            # Convert month names to numbers
            month_dict = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            depart_month_num = month_dict.get(depart_month.lower(), 1)
            return_month_num = month_dict.get(return_month.lower(), 1)
            
            # Format dates in YYYY-MM-DD format
            depart_date = f"{current_year}-{depart_month_num:02d}-{depart_day:02d}"
            return_date = f"{current_year}-{return_month_num:02d}-{return_day:02d}"
        
        # Extract number of passengers
        passengers_match = re.search(r'(\d+)\s+(?:person|people|passenger|passengers|traveler|travelers|adult|adults)', user_query, re.IGNORECASE)
        num_passengers = int(passengers_match.group(1)) if passengers_match else 1
        
        # Extract budget
        budget_match = re.search(r'budget\s+(?:is\s+)?(?:[\$\€\£])?(\d+(?:,\d+)?(?:\.\d+)?)', user_query, re.IGNORECASE)
        total_budget = float(budget_match.group(1).replace(',', '')) if budget_match else None
        
        # Set default flight budget to 40% of total budget if provided
        flight_budget = None
        if total_budget:
            flight_budget = total_budget * 0.4
        
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": depart_date,
            "return_date": return_date,
            "passengers": num_passengers,
            "total_budget": total_budget,
            "flight_budget": flight_budget
        }
        
    def get_flights(self, origin, destination, departure_date, return_date, currency="USD", num_passengers=1, max_price=None):
        """
        Search for flights using the Skyscanner API via RapidAPI.
        
        Args:
            origin (str): Origin airport or city code (e.g., 'NYC')
            destination (str): Destination airport or city code (e.g., 'LAX')
            departure_date (str): Departure date in YYYY-MM-DD format
            return_date (str): Return date in YYYY-MM-DD format
            currency (str): Currency code (default: 'USD')
            num_passengers (int): Number of passengers (default: 1)
            max_price (float): Maximum price per ticket (default: None)
            
        Returns:
            dict: Flight search results
        """
        try:
            # Format for API request
            origin_code = self._get_location_code(origin)
            destination_code = self._get_location_code(destination)
            
            if not origin_code or not destination_code:
                return {"error": "Could not determine airport codes for locations"}
            
            url = "https://skyscanner-api.p.rapidapi.com/v3/flights/live/search/create"
            
            payload = {
                "query": {
                    "market": "US",
                    "locale": "en-US",
                    "currency": currency,
                    "queryLegs": [
                        {
                            "originPlaceId": {"iata": origin_code},
                            "destinationPlaceId": {"iata": destination_code},
                            "date": {
                                "year": int(departure_date.split('-')[0]),
                                "month": int(departure_date.split('-')[1]),
                                "day": int(departure_date.split('-')[2])
                            }
                        },
                        {
                            "originPlaceId": {"iata": destination_code},
                            "destinationPlaceId": {"iata": origin_code},
                            "date": {
                                "year": int(return_date.split('-')[0]),
                                "month": int(return_date.split('-')[1]),
                                "day": int(return_date.split('-')[2])
                            }
                        }
                    ],
                    "adults": num_passengers,
                    "childrenAges": [],
                    "cabinClass": "CABIN_CLASS_ECONOMY",
                    "excludedAgentsIds": [],
                    "includedAgentsIds": [],
                    "includedCarriersIds": [],
                    "excludedCarriersIds": []
                }
            }
            
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "skyscanner-api.p.rapidapi.com"
            }
            
            logger.info(f"Sending flight search request for {origin_code} to {destination_code}")
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                flight_data = response.json()
                
                # Filter by max price if specified
                if max_price is not None:
                    filtered_flights = self._filter_flights_by_price(flight_data, max_price)
                    return filtered_flights
                
                return flight_data
            else:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                return {"error": f"API request failed with status code {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Error searching for flights: {str(e)}")
            return {"error": str(e)}
    
    def _get_location_code(self, location_name):
        """
        Convert a location name to an airport/city code using the Skyscanner API.
        
        Args:
            location_name (str): Location name (e.g., 'New York', 'Dallas')
            
        Returns:
            str: IATA code for the location (e.g., 'NYC', 'DFW')
        """
        # Common city to airport code mappings
        common_cities = {
            "new york": "NYC",
            "los angeles": "LAX",
            "chicago": "ORD",
            "houston": "IAH",
            "dallas": "DFW",
            "phoenix": "PHX",
            "san antonio": "SAT",
            "san diego": "SAN",
            "san francisco": "SFO",
            "austin": "AUS",
            "seattle": "SEA",
            "denver": "DEN",
            "washington": "IAD",
            "boston": "BOS",
            "miami": "MIA",
            "atlanta": "ATL",
            "las vegas": "LAS",
            "philadelphia": "PHL",
            "detroit": "DTW",
            "portland": "PDX"
        }
        
        # Try to match location with common cities
        location_lower = location_name.lower()
        for city, code in common_cities.items():
            if city in location_lower or location_lower in city:
                return code
                
        # If no match found, make API call to get location code
        try:
            url = "https://skyscanner-api.p.rapidapi.com/v3/autosuggest/flights"
            
            querystring = {"query": location_name}
            
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "skyscanner-api.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, params=querystring)
            
            if response.status_code == 200:
                locations = response.json().get("places", [])
                if locations:
                    # Return the IATA code of the first match
                    return locations[0].get("iata")
            
            # If API fails or no results, return empty
            logger.warning(f"Could not find airport code for {location_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting location code: {str(e)}")
            return None
    
    def _filter_flights_by_price(self, flight_data, max_price):
        """Filter flights by maximum price."""
        if not flight_data or "itineraries" not in flight_data:
            return flight_data
            
        filtered_itineraries = []
        for itinerary in flight_data.get("itineraries", []):
            price = itinerary.get("price", {}).get("amount")
            if price and price <= max_price:
                filtered_itineraries.append(itinerary)
                
        # Replace original itineraries with filtered ones
        flight_data["itineraries"] = filtered_itineraries
        return flight_data
    
    def process_flights_for_response(self, flight_data, num_results=3):
        """
        Process flight data into a readable format for the response.
        
        Args:
            flight_data (dict): Flight data from API
            num_results (int): Number of flight options to return
            
        Returns:
            list: Formatted flight options
        """
        if "error" in flight_data:
            return [{"error": flight_data["error"]}]
            
        formatted_flights = []
        
        itineraries = flight_data.get("itineraries", [])
        if not itineraries:
            return [{"info": "No flights found matching your criteria"}]
            
        # Sort by price
        itineraries.sort(key=lambda x: x.get("price", {}).get("amount", float('inf')))
        
        # Take the top N results
        top_results = itineraries[:num_results]
        
        # Format each result
        for idx, itinerary in enumerate(top_results, 1):
            price = itinerary.get("price", {})
            legs = itinerary.get("legs", [])
            
            outbound = legs[0] if legs else {}
            inbound = legs[1] if len(legs) > 1 else {}
            
            flight_option = {
                "option": idx,
                "price": f"{price.get('amount')} {price.get('currency', 'USD')}",
                "outbound": {
                    "departure": outbound.get("departure"),
                    "arrival": outbound.get("arrival"),
                    "duration": f"{outbound.get('durationInMinutes', 0)} minutes",
                    "carrier": outbound.get("carriers", {}).get("marketing", [{}])[0].get("name", "Unknown")
                }
            }
            
            if inbound:
                flight_option["inbound"] = {
                    "departure": inbound.get("departure"),
                    "arrival": inbound.get("arrival"),
                    "duration": f"{inbound.get('durationInMinutes', 0)} minutes",
                    "carrier": inbound.get("carriers", {}).get("marketing", [{}])[0].get("name", "Unknown")
                }
                
            formatted_flights.append(flight_option)
            
        return formatted_flights

    def get_flight_recommendations(self, user_query):
        """
        Process a user query and return flight recommendations.
        
        Args:
            user_query (str): User's travel query
            
        Returns:
            dict: Flight recommendations and extracted information
        """
        # Extract flight details from user query
        flight_details = self.extract_flight_details(user_query)
        
        # Check if required information is available
        if not flight_details["destination"]:
            return {
                "status": "incomplete",
                "message": "Could not determine your destination. Please specify where you want to fly to.",
                "extracted_info": flight_details
            }
        
        if not flight_details["departure_date"] or not flight_details["return_date"]:
            return {
                "status": "incomplete",
                "message": "Could not determine your travel dates. Please specify when you want to travel.",
                "extracted_info": flight_details
            }
            
        # If origin is missing, we need to ask for it
        if not flight_details["origin"]:
            return {
                "status": "incomplete",
                "message": "Could not determine your departure city. Please specify where you're flying from.",
                "extracted_info": flight_details
            }
            
        # Call the flight search API
        flights = self.get_flights(
            flight_details["origin"],
            flight_details["destination"],
            flight_details["departure_date"],
            flight_details["return_date"],
            num_passengers=flight_details["passengers"],
            max_price=flight_details["flight_budget"]
        )
        
        # Process flight results
        flight_options = self.process_flights_for_response(flights)
        
        return {
            "status": "success",
            "message": f"Found {len(flight_options)} flight options for your trip to {flight_details['destination']}.",
            "extracted_info": flight_details,
            "flight_options": flight_options,
            "budget_note": f"Note: These prices are for {flight_details['passengers']} passenger(s)." if flight_details["passengers"] > 1 else "Note: This price is for 1 passenger."
        }


# Example usage
if __name__ == "__main__":
    # Example query
    query = "plan me a 3 day trip to Dallas, Texas from July 10th to July 13th. I like cars, guns, and viewpoints. Budget is 500."
    
    # Initialize and test the flight agent
    agent = FlightAgent()
    result = agent.get_flight_recommendations(query)
    
    # Print the results
    print("Flight Recommendations:")
    print(result)
