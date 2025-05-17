import os
import json
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flight_agent")

# Groq config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# FlyScraper config
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

class FlightAgent:
    def __init__(self):
        self.api_key = RAPIDAPI_KEY
        self.groq = Groq(api_key=GROQ_API_KEY)

        self.sky_id_map = {
            "new york": "NYCA",
            "dallas": "DFWA",
            "paris": "PARI",
            "los angeles": "LAXA",
            "san francisco": "SFOA"
            # Add more mappings as needed
        }

    def _get_sky_id(self, city):
        city = city.lower().strip()
        return self.sky_id_map.get(city, city.upper() + "A")

    def extract_with_groq(self, user_query):
        prompt = f"""
Extract structured flight search info from the query below.
Return a JSON like this:
{{
  "originCity": "New York",
  "destinationCity": "Dallas",
  "departureDate": "2025-07-10",
  "returnDate": "2025-07-13",
  "passengers": 2
}}

Query: {user_query}
"""
        try:
            res = self.groq.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            content = res.choices[0].message.content.strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"GROQ parsing error: {e}")
            return {}

    def get_flights(self, origin, destination, departure_date, return_date=None, passengers=1):
        url = "https://flyscraper.p.rapidapi.com/flight/search"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "flyscraper.p.rapidapi.com"
        }

        params = {
            "originSkyId": self._get_sky_id(origin),
            "destinationSkyId": self._get_sky_id(destination),
            "departureDate": departure_date,
            "adults": passengers,
            "cabinClass": "economy",
            "currency": "USD",
            "sort": "best"
        }

        logger.info(f"Querying FlyScraper: {params}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            logger.error(f"FlyScraper error: {e}")
            return {"error": str(e)}

    def format_response_with_groq(self, user_query, flight_data):
        prompt = f"""
You are a travel agent. Based on this user request:
"{user_query}"

And this JSON flight data:
{json.dumps(flight_data)}

Respond with a conversational summary. If no flights are found or status is 'incomplete', explain that politely and suggest trying again.
"""
        try:
            res = self.groq.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq formatting error: {e}")
            return "Sorry, I couldn’t interpret the flight data properly."

    def get_flight_recommendations(self, user_query):
        # Step 1: Use Groq to extract structure
        extracted = self.extract_with_groq(user_query)
        logger.info(f"Extracted from Groq: {extracted}")

        if not all([extracted.get("originCity"), extracted.get("destinationCity"), extracted.get("departureDate")]):
            return {"error": "Missing info in extracted Groq data.", "raw": extracted}

        # Step 2: Call FlyScraper
        flights = self.get_flights(
            extracted["originCity"],
            extracted["destinationCity"],
            extracted["departureDate"],
            extracted.get("returnDate"),
            extracted.get("passengers", 1)
        )

        # Step 3: Format result via Groq
        reply = self.format_response_with_groq(user_query, flights)

        return {
            "structured_query": extracted,
            "flights_raw": flights,
            "chatbot_response": reply
        }

# Example usage
if __name__ == "__main__":
    agent = FlightAgent()
    user_input = "plan me a 3 day trip to Dallas, Texas from New York from July 10th to July 13th, 2025. Budget is 500 for 2 people"
    result = agent.get_flight_recommendations(user_input)
    print(json.dumps(result, indent=2))
