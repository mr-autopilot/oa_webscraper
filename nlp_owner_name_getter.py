import re
import trafilatura
import serpapi
from .places_api import SERP_KEY


def contains_any_of(string, arr):
    for i in arr:
        if i in string:
            return True

    return False


club = input("Name of club:\n")

good_positions = [
    "manager",
    "ceo",
    "director",
    "president",
    "vp",
    "founder",
    "owner",
    "chief",
    "partner",
]

params = {
    "engine": "google_light",
    "q": f"{club} owner",
    "api_key": SERP_KEY,
}

club_contact = "Not Found"
club_contact_linkedin = "Not Found"

search = serpapi.search(params)
results = search.as_dict()

link_results = results["organic_results"]

best_res = {}
club_clean = club.lower().strip()
if len(link_results) > 0:
    best_res = link_results[0]
    for link in link_results:
        link_clean = link["title"].lower()
        if club_clean in link_clean or contains_any_of(
            link["snippet"].lower(), good_positions
        ):
            club_contact_linkedin = link["link"]
            best_res = link
            break

print(link_results)
print(best_res)
