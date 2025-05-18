import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from groq_api import groq_ai_call

# Load environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

class FlightAgent:
    def __init__(self):
        """Initialize the flight agent with API credentials and SkyID mappings."""
        self.api_key = RAPIDAPI_KEY
        if not self.api_key:
            print("WARNING: RAPIDAPI_KEY is not set. API calls will fail.")
        
        # Common city to SkyID mappings
        self.sky_id_map = {
            "new york": "NYCA",
            "los angeles": "LAXA",
            "chicago": "CHIA",
            "houston": "HOUA",
            "dallas": "DFWA",
            "phoenix": "PHXA",
            "san antonio": "SATA",
            "san diego": "SANA",
            "san francisco": "SFOA",
            "austin": "AUSA",
            "seattle": "SEAA",
            "denver": "DENA",
            "washington": "WASA",
            "boston": "BOSA",
            "miami": "MIAA",
            "atlanta": "ATLA",
            "las vegas": "LASA",
            "philadelphia": "PHLA",
            "detroit": "DETA",
            "portland": "PDXA",
            "paris": "PARI"
        }
        
    def _get_sky_id(self, city):
        """Convert city name to SkyScanner skyId format."""
        if not city:
            return None
            
        city = city.lower().strip()
        return self.sky_id_map.get(city, city.upper() + "A")  # Fallback format

    def extract_flight_parameters(self, user_query):
        """Use Groq LLM to extract structured flight parameters from user query."""
        prompt = f"""
        Extract the following flight parameters from the user input and return ONLY valid JSON (no markdown or explanation):
        - originCity (the departure city)
        - destinationCity (the arrival city)
        - departureDate (format YYYY-MM-DD)
        - returnDate (format YYYY-MM-DD, optional)
        - passengers (number of passengers, default to 1)
        - cabinClass (economy, business, or first, default to economy)
        
        Assume dates are in MM/DD/YYYY format and convert to YYYY-MM-DD.
        If dates aren't specified, assume they're for next month.
        
        User input: {user_query}
        
        Respond with JSON only.
        """
        
        try:
            response = groq_ai_call(prompt)
            # Parse the JSON response
            return json.loads(response)
        except Exception as e:
            print(f"Error extracting flight parameters: {e}")
            return {}

    def get_flights(self, params):
        """
        Search for flights using the FlyScraper API with proper parameters
        """
        # Extract required parameters
        origin = params.get("originCity")
        destination = params.get("destinationCity")
        departure_date = params.get("departureDate")
        return_date = params.get("returnDate")
        passengers = params.get("passengers", 1)
        cabin_class = params.get("cabinClass", "economy")
        
        # Validate required parameters
        if not all([origin, destination, departure_date]):
            return {"error": "Missing required parameters (origin, destination, or departure date)"}
        
        # Convert city names to SkyIDs
        origin_sky_id = self._get_sky_id(origin)
        dest_sky_id = self._get_sky_id(destination)
        
        if not origin_sky_id or not dest_sky_id:
            return {"error": "Failed to map city names to SkyIDs"}

        url = "https://flyscraper.p.rapidapi.com/flight/search"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "flyscraper.p.rapidapi.com"
        }
        
        # Set up query parameters according to API documentation
        api_params = {
            "originSkyId": origin_sky_id,
            "destinationSkyId": dest_sky_id,
            "departureDate": departure_date,
            "adults": passengers,
            "cabinClass": cabin_class.lower(),
            "currency": "USD",
            "sort": "best"  # Default to best flights
        }

        print(f"Searching flights: {origin_sky_id} -> {dest_sky_id} on {departure_date}")
        
        try:
            response = requests.get(url, headers=headers, params=api_params)
            print(f"API request URL: {response.url}")
            response.raise_for_status()
            
            data = response.json()
            
            # Process the flight results
            processed_flights = self._process_flight_results(data)
            return processed_flights
            
        except Exception as e:
            print(f"Error getting flights: {str(e)}")
            return {"error": str(e)}

    def _process_flight_results(self, api_response):
        """Process and simplify the flight API response."""
        try:
            # Check if we have itineraries
            itineraries = api_response.get("data", {}).get("itineraries", [])
            
            if not itineraries:
                return {"flights": [], "count": 0, "message": "No flights found"}
            
            processed_flights = []
            
            # Extract relevant flight information
            for itinerary in itineraries[:5]:  # Limit to top 5 flights
                legs = itinerary.get("legs", [])
                if not legs:
                    continue
                
                # Get first leg details
                leg = legs[0]
                
                # Extract price
                price_info = itinerary.get("pricing", {}).get("pricingOptions", [{}])[0]
                price = price_info.get("price", {}).get("amount", "N/A")
                
                # Extract airline info
                carriers = leg.get("carriers", {})
                marketing = carriers.get("marketing", [{}])[0]
                airline_name = marketing.get("name", "Unknown Airline")
                flight_number = marketing.get("flightNumber", "")
                
                # Extract times
                departure_time = leg.get("departure", {}).get("time", "")
                arrival_time = leg.get("arrival", {}).get("time", "")
                
                # Extract stops
                stop_count = leg.get("stopCount", 0)
                duration = leg.get("durationInMinutes", 0)
                
                # Format duration to hours and minutes
                hours, minutes = divmod(duration, 60)
                duration_formatted = f"{hours}h {minutes}m"
                
                # Get booking URL or link information if available
                booking_info = price_info.get("url", "") or price_info.get("deepLink", "")
                
                processed_flight = {
                    "airline": airline_name,
                    "flightNumber": flight_number,
                    "price": f"${price}",
                    "departureTime": departure_time,
                    "arrivalTime": arrival_time,
                    "stops": stop_count,
                    "duration": duration_formatted,
                    "bookingLink": booking_info,
                    "itineraryId": itinerary.get("id", "")
                }
                
                processed_flights.append(processed_flight)
            
            return {
                "flights": processed_flights,
                "count": len(processed_flights)
            }
            
        except Exception as e:
            print(f"Error processing flight results: {str(e)}")
            return {"flights": [], "count": 0, "error": str(e)}

    def summarize_flights(self, flight_data, params, user_query):
        """Generate a user-friendly summary of flight options."""
        if "error" in flight_data:
            return f"Sorry, there was an error finding flights: {flight_data['error']}"
            
        flights = flight_data.get("flights", [])
        if not flights:
            return "Sorry, no flights were found matching your criteria."
            
        # Create a nice summary with markdown formatting
        summary = f"### Flight Options from {params.get('originCity')} to {params.get('destinationCity')}\n"
        summary += f"🗓️ Departure: {params.get('departureDate')}\n\n"
        
        for i, flight in enumerate(flights, 1):
            summary += f"**Option {i}: {flight['airline']}** - {flight['flightNumber']}\n"
            summary += f"💲 Price: {flight['price']}\n"
            summary += f"⏰ Departure: {flight['departureTime']} → Arrival: {flight['arrivalTime']}\n"
            summary += f"⏱️ Duration: {flight['duration']} | Stops: {flight['stops']}\n"
            
            if flight.get('bookingLink'):
                summary += f"[🔗 Book this flight]({flight['bookingLink']})\n"
                
            summary += "\n"
            
        return summary
            
    def get_flight_recommendations(self, user_query):
        """Main function to extract details from query and get flight recommendations."""
        # Extract parameters from user query using Groq
        params = self.extract_flight_parameters(user_query)
        print(f"Extracted flight parameters: {params}")
        
        # Get flights based on extracted parameters
        flight_data = self.get_flights(params)
        
        # Generate a user-friendly summary
        summary = self.summarize_flights(flight_data, params, user_query)
        
        return {
            "parameters": params,
            "flight_data": flight_data,
            "summary": summary
        }


# Example usage
if __name__ == "__main__":
    agent = FlightAgent()
    query = input("Tell me about your flight plans: ")
    result = agent.get_flight_recommendations(query)
    print("\n" + result["summary"])
