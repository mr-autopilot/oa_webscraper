import re
import trafilatura
import serpapi


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
]

params = {
    "engine": "google_light",
    "q": f"{club} owner",
    "api_key": "9e82271ac2c170fed452de0dfd81741a7c060d0821dd0adb48c821c3d81b5f67",
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
