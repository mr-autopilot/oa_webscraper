import requests
from dotenv import load_dotenv
import os

from .enrichment import naive_email_search

# Load .env file (contains API keys and output path)
load_dotenv(".env")

# Environment variables
API_KEY = os.getenv("API_KEY")
SERP_KEY = os.getenv("SERP_KEY")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")

# Endpoint for Places Text Search (used to retrieve Place IDs)
TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Headers required for initial text search request
TEXT_SEARCH_HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.id",
}

# Headers required for place details enrichment request
DETAILS_HEADER = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "displayName,shortFormattedAddress,nationalPhoneNumber,websiteUri,addressComponents",
}

# Base URL for individual Place Details queries
DETAILS_URL = "https://places.googleapis.com/v1/places/"

# Substrings that signal a website is likely irrelevant or civic (for filtering)
WEB_BLACKLIST = [
    "facilities",
    "facility",
    "parks",
    ".gov",
    ".org",
    "county",
    "clerk",
    "court",
    "circuit",
    "district",
    ".edu",
    "center",
    "centre",
    "community",
    "school",
    "rec",
    "cityof",
    "campground",
    # apparently subways get grabbed pretty regularly
    "subway",
    "store",
    "townof",
    "fairgrounds",
    "sportsmen",
]

# Substrings that signal a name is likely irrelevant
NAME_BLACKLIST = [
    "clerk",
    "court",
    "circuit",
    "district",
    "center",
    "centre",
    "community",
    "school",
    "campground",
    # apparently subways get grabbed pretty regularly
    "subway",
    "store",
    "fairgrounds",
    "sportsmen",
    "gun",
    "golf",
    "fair",
    "archery",
    "senior",
    # paradoxically, to avoid any public courts
    "pickleball courts",
]


def dedup_by_ids(places):
    # Deduplicates places by their ID (used after merging multiple search results)
    out = []
    for place in places:
        if not id_in_list(place["id"], out):
            out.append(place)

    return out


def id_in_list(id, places):
    # Checks if a given ID is already in a list of places
    for i in places:
        if id == i["id"]:
            return True

    return False


def get_pickleball_clubs_in_area(area, state=""):
    print(f"Searching area {area}")

    # Sends 3 variations of text search queries to increase search coverage
    merged = []
    query1 = {
        "textQuery": f"indoor pickleball in {area}, {state}",
    }

    query2 = {
        "textQuery": f"pickleball clubs in {area}, {state}",
    }

    query3 = {
        "textQuery": f"pickleball in {area}, {state}",
    }

    # All of these are free (id-only) queries — results return Place IDs
    resp1 = requests.post(TEXT_SEARCH_URL, json=query1, headers=TEXT_SEARCH_HEADERS)

    resp2 = requests.post(TEXT_SEARCH_URL, json=query2, headers=TEXT_SEARCH_HEADERS)

    resp3 = requests.post(TEXT_SEARCH_URL, json=query3, headers=TEXT_SEARCH_HEADERS)

    # Merge all results
    merged.extend(resp1.json().get("places", {}))
    merged.extend(resp2.json().get("places", {}))
    merged.extend(resp3.json().get("places", {}))

    # Remove duplicates
    merged_places = dedup_by_ids(merged)

    return merged_places


def get_clubs_in_list_of_areas(areas, state):
    # Wrapper to run get_pickleball_clubs_in_area across a list of counties
    merged = []

    for area in areas:
        area_res = get_pickleball_clubs_in_area(area, state=state)
        merged.extend(area_res)

    merged = dedup_by_ids(merged)
    return merged


def enrich_individual_result(id_json):
    # Fetch full Place Details (this is the $0.02 enrichment call)
    id = id_json["id"]
    resp = requests.get(
        f"{DETAILS_URL}{id}",
        headers=DETAILS_HEADER,
    )

    details = resp.json()

    # Extract individual fields (some may be missing)
    name = details.get("displayName", "Not Available")
    if not name == "Not Available":
        name = name["text"]

    addy = details.get("shortFormattedAddress", "Not Available")
    addy_comps = details.get("addressComponents")

    website = details.get("websiteUri", "Not Available")

    number = details.get("nationalPhoneNumber", "Not Available")

    print(f"Lead found: {name}")
    return {
        "name": name,
        "address": addy,
        "address_components": addy_comps,
        "phone": number,
        "website": website,
        "email": "",
    }


def enrich_location_list(loc_ids, state: None | str = None):
    # Loops through all Place IDs and enriches + filters them
    output = []
    for id in loc_ids:
        result = enrich_individual_result(id)

        # Check for filtered words in website or name
        contains_blacklisted = in_blacklist(
            WEB_BLACKLIST, result["website"]
        ) or in_blacklist(NAME_BLACKLIST, result["website"])

        location_ok = True

        if state:
            # If doing a full-state scrape, verify business is actually located in the target state (Google will sometimes fudge bordering counties)
            location_ok = state_in_address_components(
                state, result["address_components"]
            )

        # Apply core filtering: skip if missing key data or blacklisted
        if (
            result["website"] != "Not Available"
            and result["phone"] != "Not Available"
            and not contains_blacklisted
            and location_ok
        ):
            # Scrape email from website (if any)
            result["email"] = naive_email_search(result["website"])
            output.append(result)

    return output


def in_blacklist(blacklist, string: str):
    # Returns True if any blacklist term appears in string
    for word in blacklist:
        if word.lower() in string.lower():
            return True

    return False


def state_in_address_components(state, address_comps):
    # Checks if the state's name appears in the addressComponents block
    for i in address_comps:
        if i["longText"].lower() == state.lower():
            return True

    return False


def write_locs_as_csv(loc_lists, timestamp):
    # Save results to CSV with semi-colon delimiters
    with open(f"{OUTPUT_DIR}/enriched_{timestamp}.csv", "w") as csv:
        csv.write("name; phone number; website; business email; street address\n")

        for item in loc_lists:
            csv.write(
                f"{item['name']};{item['phone']};{item['website']};{item['email']};{item['address']}\n"
            )
