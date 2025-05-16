# main.py for VoyAgent API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from typing import Dict, Any, List, Optional
import random
from datetime import datetime, timedelta
import os

# Initialize FastAPI app
app = FastAPI(title="VoyAgent API", description="AI Travel Concierge API")

# Add CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace with your actual API key
# In production, use environment variables: os.environ.get("GROK_API_KEY")
GROK_API_KEY = xai-mPXLmlWr6d2g7BcNmLAiJvm1TSjAxFQvOtHR2105uq46iducE5BgMj9NbvFDnqcdhkpKMcXpk1bnk5Lo
GROQ_API_URL= https://api.groq.com/openai/v1/chat/completions  # Replace with actual Grok API URL

# ----- Models -----

class UserQuery(BaseModel):
    input: str

class TravelDetails(BaseModel):
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    interests: List[str] = []

class FlightInfo(BaseModel):
    from_city: str
    to_city: str
    departure_date: str
    return_date: str
    price: float
    airline: str
    departure_time: str
    arrival_time: str
    return_departure_time: str
    return_arrival_time: str

class HotelInfo(BaseModel):
    name: str
    location: str
    price_per_night: float
    total_price: float
    rating: float
    amenities: List[str]
    image_url: str

class ItineraryDay(BaseModel):
    day: int
    date: str
    morning: str
    afternoon: str
    evening: str
    estimated_cost: float

class TripPlan(BaseModel):
    travel_details: TravelDetails
    flight: FlightInfo
    hotel: HotelInfo
    itinerary: List[ItineraryDay]
    remaining_budget: float

# ----- Helper Functions -----

def parse_travel_query(query: str) -> Dict:
    """Parse the travel query using OpenAI to extract structured data"""
    system_prompt = """
    You are an AI travel assistant. Extract the following information from the user's travel query:
    - destination (city or country)
    - start_date (in YYYY-MM-DD format if specific, or month if general)
    - end_date (in YYYY-MM-DD format if specific, or duration if general)
    - budget (in USD)
    - interests (list of activities or preferences)
    
    Return ONLY a valid JSON object with these fields. If a field cannot be determined, use null.
    Example: {"destination": "Paris", "start_date": "2025-06-10", "end_date": "2025-06-15", "budget": 2000, "interests": ["art", "food"]}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.1,  # Lower temperature for more consistent formatting
        )
        result = response.choices[0].message.content.strip()
        
        # Parse the JSON response
        try:
            travel_details = json.loads(result)
            return travel_details
        except json.JSONDecodeError:
            # If we can't parse the JSON, try to extract what we can
            return {
                "destination": "Unknown",
                "start_date": None,
                "end_date": None, 
                "budget": None,
                "interests": []
            }
            
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

def format_date(date_str: str) -> str:
    """Converts various date formats to YYYY-MM-DD"""
    if not date_str:
        # Default to next month if no date provided
        future_date = datetime.now() + timedelta(days=30)
        return future_date.strftime("%Y-%m-%d")
    
    # If it's already in YYYY-MM-DD format, return as is
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str
        
    # Otherwise, handle general dates like "June", "June 2025", etc.
    # This is simplified - in a real app you'd want more robust date parsing
    current_year = datetime.now().year
    
    if "june" in date_str.lower():
        return f"{current_year}-06-15"  # Middle of June
    elif "july" in date_str.lower():
        return f"{current_year}-07-15"
    elif "august" in date_str.lower():
        return f"{current_year}-08-15"
    else:
        # Default to next month
        future_date = datetime.now() + timedelta(days=30)
        return future_date.strftime("%Y-%m-%d")

# ----- API Endpoints -----

@app.post("/analyze")
def analyze_query(q: UserQuery):
    """Determine if a query is travel-related and extract details if it is"""
    system_prompt = (
        "You're an AI that determines whether a user's message is about travel planning. "
        "If it is about planning a trip, respond with 'TRAVEL'. "
        "If it's not about planning a trip, respond with 'NOT_TRAVEL'."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": q.input}
            ],
            temperature=0.1,  # Lower temperature for more deterministic results
        )
        
        result = response.choices[0].message.content.strip()
        
        if "TRAVEL" in result:
            # This is a travel query, extract details
            travel_details = parse_travel_query(q.input)
            return {"is_travel": True, "details": travel_details}
        else:
            # Not a travel query
            return {"is_travel": False, "details": None}
            
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze query: {str(e)}")

@app.post("/get_flights")
def get_flights(details: TravelDetails):
    """Get flight options based on travel details (mocked)"""
    # In a real implementation, this would call the Skyscanner or Amadeus API
    
    # For the mock, we'll generate a random flight
    airlines = ["SkyWings", "Global Air", "Oceanic", "TransWorld", "Star Airways"]
    from_city = "New York"  # Assuming departure from NY for simplicity
    
    # Format dates properly
    departure_date = format_date(details.start_date)
    return_date = format_date(details.end_date)
    
    # Calculate a realistic price based on destination
    if details.destination.lower() in ["paris", "london", "rome", "europe"]:
        base_price = random.uniform(600, 1200)
    elif details.destination.lower() in ["tokyo", "bangkok", "seoul", "asia"]:
        base_price = random.uniform(900, 1800)
    else:
        base_price = random.uniform(300, 900)
        
    # Adjust price based on budget (lower budget = cheaper flights)
    if details.budget:
        price_factor = min(1.0, details.budget / 3000)
        price = base_price * price_factor
    else:
        price = base_price
        
    # Mock flight times
    departure_time = "08:30"
    arrival_time = "14:45"
    return_departure_time = "16:20"
    return_arrival_time = "22:35"
    
    flight = {
        "from_city": from_city,
        "to_city": details.destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "price": round(price, 2),
        "airline": random.choice(airlines),
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "return_departure_time": return_departure_time,
        "return_arrival_time": return_arrival_time
    }
    
    return {"flights": [flight]}

@app.post("/get_hotels")
def get_hotels(details: TravelDetails):
    """Get hotel options based on travel details (mocked)"""
    # In a real implementation, this would call Expedia, Booking.com or Amadeus API
    
    # For the mock, we'll generate a few random hotels
    hotel_templates = [
        {
            "name": "Grand Plaza Hotel",
            "rating": 4.5,
            "amenities": ["Pool", "Spa", "Restaurant", "Free WiFi"],
            "image_url": "https://example.com/hotel1.jpg"
        },
        {
            "name": "Riverside Inn",
            "rating": 3.8,
            "amenities": ["Free WiFi", "Continental Breakfast", "Fitness Center"],
            "image_url": "https://example.com/hotel2.jpg"
        },
        {
            "name": "City Center Suites",
            "rating": 4.2,
            "amenities": ["Kitchen", "Workspace", "Laundry", "Free WiFi"],
            "image_url": "https://example.com/hotel3.jpg"
        },
        {
            "name": "Heritage Boutique Hotel",
            "rating": 4.7,
            "amenities": ["Fine Dining", "Spa", "Concierge", "Free WiFi"],
            "image_url": "https://example.com/hotel4.jpg"
        }
    ]
    
    # Calculate number of nights
    try:
        start_date = datetime.strptime(format_date(details.start_date), "%Y-%m-%d")
        end_date = datetime.strptime(format_date(details.end_date), "%Y-%m-%d")
        nights = (end_date - start_date).days
        if nights <= 0:
            nights = 3  # Default to 3 nights if dates are invalid
    except:
        nights = 3  # Default
    
    # Calculate price ranges based on destination, budget, and hotel quality
    hotels = []
    for template in hotel_templates:
        if details.destination.lower() in ["paris", "london", "tokyo", "new york"]:
            base_price = random.uniform(150, 300) * (template["rating"] / 3.5)
        else:
            base_price = random.uniform(80, 200) * (template["rating"] / 3.5)
            
        # Adjust price based on budget
        if details.budget:
            budget_factor = min(1.0, details.budget / 3000)
            price_per_night = base_price * budget_factor
        else:
            price_per_night = base_price
            
        hotel = {
            **template,
            "location": f"Downtown {details.destination}",
            "price_per_night": round(price_per_night, 2),
            "total_price": round(price_per_night * nights, 2)
        }
        hotels.append(hotel)
    
    # Sort by price (ascending)
    hotels.sort(key=lambda h: h["price_per_night"])
    
    return {"hotels": hotels}

@app.post("/get_itinerary")
def get_itinerary(details: TravelDetails):
    """Generate a day-by-day itinerary based on travel details"""
    # Calculate number of days
    try:
        start_date = datetime.strptime(format_date(details.start_date), "%Y-%m-%d")
        end_date = datetime.strptime(format_date(details.end_date), "%Y-%m-%d")
        days = (end_date - start_date).days + 1
        if days <= 0:
            days = 3  # Default to 3 days if dates are invalid
    except:
        days = 3  # Default
    
    interests_str = ", ".join(details.interests) if details.interests else "sightseeing and local culture"
    budget_str = f"{details.budget} USD" if details.budget else "moderate"
    
    # Use OpenAI to generate the itinerary
    system_prompt = f"""
    You are an expert travel planner. Create a detailed day-by-day itinerary for a trip to {details.destination} for {days} days.
    The traveler is interested in: {interests_str}
    Budget: {budget_str}
    
    For each day provide:
    1. Morning activity (9am-12pm)
    2. Afternoon activity (12pm-5pm)
    3. Evening activity (5pm-10pm)
    4. Estimated cost for the day's activities in USD
    
    Format your response as a JSON array with objects for each day following this exact structure:
    [
      {{
        "day": 1,
        "date": "2025-06-10",
        "morning": "Visit the Louvre Museum and see the Mona Lisa",
        "afternoon": "Lunch at a local bistro, then walk along Seine River",
        "evening": "Dinner at Le Jules Verne restaurant with Eiffel Tower views",
        "estimated_cost": 120
      }},
      ...
    ]
    Return ONLY the valid JSON array, no other text.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create an itinerary for {days} days in {details.destination}."}
            ],
            temperature=0.7,  # More creative for itineraries
        )
        
        result = response.choices[0].message.content.strip()
        
        # Extract the JSON from the response (remove any markdown code blocks if present)
        result = result.replace("```json", "").replace("```", "").strip()
        
        try:
            itinerary_days = json.loads(result)
            
            # If the start date is provided, update the dates in the itinerary
            if details.start_date:
                start = datetime.strptime(format_date(details.start_date), "%Y-%m-%d")
                for i, day in enumerate(itinerary_days):
                    day_date = start + timedelta(days=i)
                    day["date"] = day_date.strftime("%Y-%m-%d")
            
            return {"itinerary": itinerary_days}
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse itinerary JSON: {e}")
            # Fallback to a simple structured itinerary
            itinerary = []
            start = datetime.strptime(format_date(details.start_date), "%Y-%m-%d") if details.start_date else datetime.now()
            
            for i in range(days):
                day_date = start + timedelta(days=i)
                itinerary.append({
                    "day": i + 1,
                    "date": day_date.strftime("%Y-%m-%d"),
                    "morning": f"Explore {details.destination} downtown area",
                    "afternoon": "Lunch and shopping at local markets",
                    "evening": "Dinner at a local restaurant",
                    "estimated_cost": 100
                })
            
            return {"itinerary": itinerary}
    
    except Exception as e:
        print(f"Error generating itinerary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate itinerary: {str(e)}")

@app.post("/plan_trip")
async def plan_trip(req: UserQuery):
    """Full trip planning endpoint that combines all steps"""
    
    # Step 1: Analyze and parse the query
    analysis = analyze_query(req)
    
    if not analysis["is_travel"]:
        return {"error": "Your query does not appear to be travel-related. Please specify destination, dates, and interests."}
    
    travel_details = analysis["details"]
    
    # Convert to proper model
    details = TravelDetails(
        destination=travel_details["destination"],
        start_date=travel_details["start_date"],
        end_date=travel_details["end_date"],
        budget=travel_details["budget"] if travel_details["budget"] else 2000,  # Default budget
        interests=travel_details["interests"] if travel_details["interests"] else []
    )
    
    # Step 2: Get flights
    flight_response = get_flights(details)
    flight = flight_response["flights"][0]  # Take first flight option
    
    # Step 3: Get hotels
    hotel_response = get_hotels(details)
    hotel = hotel_response["hotels"][0]  # Take first hotel option
    
    # Step 4: Generate itinerary
    itinerary_response = get_itinerary(details)
    itinerary = itinerary_response["itinerary"]
    
    # Step 5: Calculate remaining budget
    total_spent = flight["price"] + hotel["total_price"]
    daily_costs = sum(day["estimated_cost"] for day in itinerary)
    total_cost = total_spent + daily_costs
    remaining_budget = details.budget - total_cost if details.budget else 0
    
    # Build the complete trip plan
    trip_plan = {
        "travel_details": {
            "destination": details.destination,
            "start_date": format_date(details.start_date),
            "end_date": format_date(details.end_date),
            "budget": details.budget,
            "interests": details.interests
        },
        "flight": flight,
        "hotel": hotel,
        "itinerary": itinerary,
        "costs": {
            "flight_cost": flight["price"],
            "hotel_cost": hotel["total_price"],
            "activities_cost": daily_costs,
            "total_cost": total_cost,
            "remaining_budget": remaining_budget
        }
    }
    
    return trip_plan

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
