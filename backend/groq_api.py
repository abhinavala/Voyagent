import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

def groq_ai_call(prompt):
    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_completion_tokens": 1024,
        "top_p": 1,
        "stream": False,
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def extract_parameters_from_user_input(user_input):
    prompt = f"""
Extract the following travel parameters from the user input and return ONLY valid JSON (no markdown or explanation):
- location
- arrival_date (format YYYY-MM-DD)
- departure_date (format YYYY-MM-DD)
- guest_qty
- children_qty
- children_age (list of integers)
- travel_purpose

Assume all dates are MM/DD/YYYY and convert to YYYY-MM-DD.

User input: {user_input}
Respond with JSON only.
"""
    response = groq_ai_call(prompt)

    # Remove markdown if present
    match = re.search(r"\{.*\}", response, re.DOTALL)
    content = match.group(0) if match else response.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("Groq response is not valid JSON")

def get_best_booking_url(hotel: dict) -> str | None:
    """
    Determine the best Booking.com URL for a hotel.

    Order of preference:
    1. Direct known URL fields from API response
    2. Construct URL from hotel_slug or url_slug if available
    3. Use hotel's own website URL if valid
    4. Fallback: Google search link for hotel name + city

    Returns:
        URL string or None if no suitable URL found.
    """
    url_fields = [
        "booking_url",
        "deep_link",
        "affiliate_url",
        "url",
        "composite_url",
        "click_url",
    ]

    # Check direct URLs first
    for field in url_fields:
        url = hotel.get(field)
        if url and url.startswith("http"):
            return url

    # Try to construct Booking.com URL from slug
    slug = hotel.get("hotel_slug") or hotel.get("url_slug")
    if slug:
        return f"https://www.booking.com/hotel/us/{slug}.html"

    # Check hotel's own website URL
    website = hotel.get("hotel_website")
    if website and website.startswith("http"):
        return website

    # Last resort: Google search link
    name = hotel.get("hotel_name") or hotel.get("name")
    city = hotel.get("city") or hotel.get("location")
    if name:
        query = "+".join(name.split())
        if city:
            query += "+" + "+".join(city.split())
        return f"https://www.google.com/search?q={query}"

    return None


def summarize_hotels(hotel_data: dict, filters: dict, user_input: str) -> str:
    """
    Summarizes hotel options with booking links.

    Args:
        hotel_data: Raw hotel response from Booking.com API.
        filters: Parameters used for search (location, dates, guests).
        user_input: Original user input string.

    Returns:
        A friendly summary string with hotel names and booking URLs.
    """
    # Try common keys for hotel list
    hotels = hotel_data.get('result') or hotel_data.get('results') or hotel_data.get('properties') or []

    hotel_list = []
    for hotel in hotels[:5]:  # Limit top 5 hotels
        name = hotel.get("hotel_name", "Unnamed Hotel")
        url = get_best_booking_url(hotel)
        if url:
            hotel_list.append(f"**{name}** - [Book Here]({url})")
        else:
            hotel_list.append(f"**{name}** (No booking URL available)")

    # Compose a summary prompt or plain summary if you want:
    summary = f"Here are some hotels based on your input:\n\n" + "\n".join(hotel_list)
    return summary
