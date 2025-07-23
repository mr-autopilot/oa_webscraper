import requests
from dotenv import load_dotenv
import os

load_dotenv(".env")

API_KEY = os.getenv("API_KEY")

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

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

    name = details.get("displayName", "Not Available")
    if not name == "Not Available":
        name = name["text"]

    addy = details.get("shortFormattedAddress", "Not Available")

    website = details.get("websiteUri", "Not Available")

    number = details.get("nationalPhoneNumber", "Not Available")

    return {
        "name": name,
        "address": addy,
        "phone": number,
        "website": website,
    }


def enrich_location_list(loc_ids):
    output = []
    for id in loc_ids:
        result = enrich_individual_result(id)
        contains_facilities = (
            "facilities" in result["website"].lower()
            or "facility" in result["website"].lower()
            or "parks" in result["website"].lower()
            or ".gov" in result["website"].lower()
        )
        if (
            result["website"] != "Not Available"
            and result["phone"] != "Not Available"
            and not contains_facilities
        ):
            output.append(result)

    return output


def write_locs_as_csv(loc_lists, timestamp):
    with open(f"enriched_{timestamp}.csv", "w") as csv:
        csv.write("name; address; phone number; website\n")

        for item in loc_lists:
            csv.write(
                f"{item['name']};{item['address']};{item['phone']};{item['website']}\n"
            )
