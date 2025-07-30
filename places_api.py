import requests
from dotenv import load_dotenv
import os

from .enrichment import naive_email_search

load_dotenv(".env")

# Environment variables
API_KEY = os.getenv("API_KEY")
SERP_KEY = os.getenv("SERP_KEY")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# API Headers, as required by Google Places API
TEXT_SEARCH_HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.id",
}

DETAILS_HEADER = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "displayName,shortFormattedAddress,nationalPhoneNumber,websiteUri,addressComponents",
}

DETAILS_URL = "https://places.googleapis.com/v1/places/"

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
    "archery",
    "senior",
    # paradoxically, to avoid any public courts
    "pickleball courts",
]


def dedup_by_ids(places):
    out = []
    for place in places:
        if not id_in_list(place["id"], out):
            out.append(place)

    return out


def id_in_list(id, places):
    for i in places:
        if id == i["id"]:
            return True

    return False


def get_pickleball_clubs_in_area(area, state=""):
    print(f"Searching area {area}")

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

    resp1 = requests.post(TEXT_SEARCH_URL, json=query1, headers=TEXT_SEARCH_HEADERS)

    resp2 = requests.post(TEXT_SEARCH_URL, json=query2, headers=TEXT_SEARCH_HEADERS)

    resp3 = requests.post(TEXT_SEARCH_URL, json=query3, headers=TEXT_SEARCH_HEADERS)

    merged.extend(resp1.json().get("places", {}))
    merged.extend(resp2.json().get("places", {}))
    merged.extend(resp3.json().get("places", {}))

    merged_places = dedup_by_ids(merged)

    return merged_places


def get_clubs_in_list_of_areas(areas, state):
    merged = []

    for area in areas:
        area_res = get_pickleball_clubs_in_area(area, state=state)
        merged.extend(area_res)

    merged = dedup_by_ids(merged)
    return merged


def enrich_individual_result(id_json):
    id = id_json["id"]
    resp = requests.get(
        f"{DETAILS_URL}{id}",
        headers=DETAILS_HEADER,
    )

    details = resp.json()

    # print(details)

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
    output = []
    for id in loc_ids:
        result = enrich_individual_result(id)

        contains_blacklisted = in_blacklist(
            WEB_BLACKLIST, result["website"]
        ) or in_blacklist(NAME_BLACKLIST, result["website"])

        location_ok = True

        print(result["address_components"])
        if state:
            location_ok = state_in_address_components(
                state, result["address_components"]
            )
        print(location_ok)

        if (
            result["website"] != "Not Available"
            and result["phone"] != "Not Available"
            and not contains_blacklisted
            and location_ok
        ):
            result["email"] = naive_email_search(result["website"])
            output.append(result)

    return output


def in_blacklist(blacklist, string: str):
    for word in blacklist:
        if word.lower() in string.lower():
            return True

    return False


def state_in_address_components(state, address_comps):
    for i in address_comps:
        if i["longText"].lower() == state.lower():
            return True

    return False


def write_locs_as_csv(loc_lists, timestamp):
    with open(f"{OUTPUT_DIR}/enriched_{timestamp}.csv", "w") as csv:
        csv.write("name; address; phone number; website; email\n")

        for item in loc_lists:
            csv.write(
                f"{item['name']};{item['address']};{item['phone']};{item['website']};{item['email']}\n"
            )
