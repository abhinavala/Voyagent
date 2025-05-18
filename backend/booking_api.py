import os
import requests
from urllib.parse import urlencode

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# Bounding boxes for all 50 US states (format: "lat_min,lat_max,lon_min,lon_max")
STATE_BBOXES = {
    "alabama": "30.223334,35.008028,-88.473227,-84.888246",
    "alaska": "51.214183,71.365162,-170.224871,-129.993001",
    "arizona": "31.332177,37.00426,-114.818269,-109.045223",
    "arkansas": "33.004106,36.4996,-94.617919,-89.644395",
    "california": "32.5121,42.0126,-124.6509,-114.1315",
    "colorado": "36.992424,41.003444,-109.060253,-102.041524",
    "connecticut": "40.95017,42.0506,-73.727775,-71.786994",
    "delaware": "38.451013,39.839007,-75.789,-75.048939",
    "florida": "24.396308,31.000888,-87.634938,-79.974307",
    "georgia": "30.357851,35.000659,-85.605165,-80.839729",
    "hawaii": "18.86546,22.2356,-160.2471,-154.8066",
    "idaho": "41.988057,49.001146,-117.243027,-111.043564",
    "illinois": "36.970298,42.508481,-91.513079,-87.019935",
    "indiana": "37.771742,41.761141,-88.097888,-84.784579",
    "iowa": "40.375501,43.501196,-96.639704,-90.140061",
    "kansas": "36.993016,40.003162,-102.051744,-94.588413",
    "kentucky": "36.497129,39.147458,-89.571509,-81.964971",
    "louisiana": "28.928609,33.019457,-94.043147,-89.742652",
    "maine": "42.977764,47.459686,-71.083924,-66.949895",
    "maryland": "37.886775,39.723043,-79.487651,-75.048939",
    "massachusetts": "41.237964,42.886589,-73.508142,-69.928393",
    "michigan": "41.696118,48.306064,-90.418136,-82.413474",
    "minnesota": "43.499356,49.384358,-97.239209,-89.491739",
    "mississippi": "30.173943,35.004096,-91.655009,-88.09976",
    "missouri": "35.995683,40.61364,-95.774704,-89.099727",
    "montana": "44.358221,49.00139,-116.050003,-104.039138",
    "nebraska": "39.999998,43.001708,-104.053514,-95.30829",
    "nevada": "35.001857,42.002207,-120.005746,-114.039648",
    "new_hampshire": "42.697041,45.305476,-72.557247,-70.610621",
    "new_jersey": "38.928519,41.357423,-75.559614,-73.893979",
    "new_mexico": "31.332177,37.000232,-109.050173,-103.001964",
    "new_york": "40.477399,45.01585,-79.76259,-71.856214",
    "north_carolina": "33.842316,36.588117,-84.321869,-75.459534",
    "north_dakota": "45.935054,49.000574,-104.049856,-96.554507",
    "ohio": "38.403202,41.977523,-84.820159,-80.518693",
    "oklahoma": "33.615833,37.002206,-103.002565,-94.430662",
    "oregon": "41.991794,46.292035,-124.566244,-116.463104",
    "pennsylvania": "39.7198,42.26986,-80.519891,-74.689516",
    "rhode_island": "41.146339,42.018798,-71.862772,-71.12057",
    "south_carolina": "32.0346,35.2154,-83.3539,-78.54203",
    "south_dakota": "42.479635,45.94545,-104.057698,-96.436589",
    "tennessee": "34.982972,36.678118,-90.310298,-81.6469",
    "texas": "25.837377,36.500704,-106.645646,-93.508292",
    "utah": "36.997968,42.001567,-114.052962,-109.041058",
    "vermont": "42.726853,45.016659,-73.43774,-71.464555",
    "virginia": "36.540738,39.466012,-83.675553,-75.242266",
    "washington": "45.543541,49.002494,-124.848974,-116.916364",
    "west_virginia": "37.201483,39.722302,-82.644739,-77.719519",
    "wisconsin": "42.491983,47.309825,-92.888114,-86.805415",
    "wyoming": "40.994746,45.005904,-111.056888,-104.05216"
}

DEFAULT_US_BBOX = "24.396308,49.384358,-125.0,-66.93457"

def get_bounding_box(location: str) -> str:
    if not location:
        raise ValueError("Location parameter is required for bounding box lookup.")
    key = location.lower().replace(" ", "_").replace(".", "")
    return STATE_BBOXES.get(key, DEFAULT_US_BBOX)

def build_booking_url(base_url, arrival_date, departure_date, guest_qty, children_qty, children_age):
    """
    Construct the full booking URL with query parameters for dates and guests.
    Assumes arrival_date and departure_date are MM-DD and adds year 2025.
    """
    arrival_date_full = f"2025-{arrival_date}"  # Add year 2025 prefix
    departure_date_full = f"2025-{departure_date}"  # Add year 2025 prefix

    params = {
        "checkin": arrival_date_full,
        "checkout": departure_date_full,
        "group_adults": guest_qty,
        "group_children": children_qty,
    }
    if children_qty and int(children_qty) > 0:
        if isinstance(children_age, list):
            children_age_str = ",".join(str(age) for age in children_age)
        else:
            children_age_str = str(children_age)
        params["age"] = children_age_str

    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{urlencode(params)}"

def get_hotels(params: dict) -> dict:
    location = params.get("location")
    if not location:
        raise ValueError("Missing required parameter: 'location'")
    arrival_date = params.get("arrival_date")
    departure_date = params.get("departure_date")
    if not arrival_date or not departure_date:
        raise ValueError("Missing required parameters: 'arrival_date' and/or 'departure_date'")

    bbox = get_bounding_box(location)
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    children_ages = params.get("children_age", [])
    if isinstance(children_ages, list):
        children_age_str = ",".join(str(age) for age in children_ages)
    else:
        children_age_str = str(children_ages) if children_ages else ""

    querystring = {
        "room_qty": "1",
        "guest_qty": str(params.get("guest_qty", "2")),
        "children_qty": str(params.get("children_qty", "0")),
        "children_age": children_age_str,
        "bbox": bbox,
        "price_filter_currencycode": "USD",
        "languagecode": "en-us",
        "travel_purpose": params.get("travel_purpose", "leisure"),
        "order_by": "popularity",
        "arrival_date": arrival_date,
        "departure_date": departure_date,
        "categories_filter": "class::1,class::2,class::3",
        "offset": "0"
    }

    url = "https://apidojo-booking-v1.p.rapidapi.com/properties/list-by-map"
    
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()
    data = response.json()

    # Add booking_url to each hotel in the results
    guest_qty = querystring["guest_qty"]
    children_qty = querystring["children_qty"]
    children_age = querystring["children_age"]

    for hotel in data.get("result", []):
        base_url = hotel.get("url")
        if base_url:
            hotel["booking_url"] = build_booking_url(
                base_url,
                arrival_date,
                departure_date,
                guest_qty,
                children_qty,
                children_age
            )
        else:
            hotel["booking_url"] = None  # or fallback

    print("API response keys:", data.keys())
    print("Number of hotels returned:", len(data.get("result", [])))
    return data
