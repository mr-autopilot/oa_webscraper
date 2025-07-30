from flask import Flask, render_template, request, jsonify, send_file
from oa_webscraper.places_api import (
    get_pickleball_clubs_in_area,
    enrich_location_list,
    write_locs_as_csv,
    get_clubs_in_list_of_areas,
)
from oa_webscraper import counties

from oa_webscraper.places_api import OUTPUT_DIR

# Mapping of lowercase state names to lists of county names
# Used to expand a state-level search into individual county-level queries
state_counties = {
    "alabama": counties.ALABAMA_COUNTIES,
    "alaska": counties.ALASKA_COUNTIES,
    "arizona": counties.ARIZONA_COUNTIES,
    "arkansas": counties.ARKANSAS_COUNTIES,
    "california": counties.CALIFORNIA_COUNTIES,
    "colorado": counties.COLORADO_COUNTIES,
    "connecticut": counties.CONNECTICUT_COUNTIES,
    "delaware": counties.DELAWARE_COUNTIES,
    "florida": counties.FLORIDA_COUNTIES,
    "georgia": counties.GEORGIA_COUNTIES,
    "hawaii": counties.HAWAII_COUNTIES,
    "idaho": counties.IDAHO_COUNTIES,
    "illinois": counties.ILLINOIS_COUNTIES,
    "indiana": counties.INDIANA_COUNTIES,
    "iowa": counties.IOWA_COUNTIES,
    "kansas": counties.KANSAS_COUNTIES,
    "kentucky": counties.KENTUCKY_COUNTIES,
    "louisiana": counties.LOUISIANA_COUNTIES,
    "maine": counties.MAINE_COUNTIES,
    "maryland": counties.MARYLAND_COUNTIES,
    "massachusetts": counties.MASSACHUSETTS_COUNTIES,
    "michigan": counties.MICHIGAN_COUNTIES,
    "minnesota": counties.MINNESOTA_COUNTIES,
    "mississippi": counties.MISSISSIPPI_COUNTIES,
    "missouri": counties.MISSOURI_COUNTIES,
    "montana": counties.MONTANA_COUNTIES,
    "nebraska": counties.NEBRASKA_COUNTIES,
    "nevada": counties.NEVADA_COUNTIES,
    "new hampshire": counties.NEW_HAMPSHIRE_COUNTIES,
    "new jersey": counties.NEW_JERSEY_COUNTIES,
    "new mexico": counties.NEW_MEXICO_COUNTIES,
    "new york": counties.NEW_YORK_COUNTIES,
    "north carolina": counties.NORTH_CAROLINA_COUNTIES,
    "north dakota": counties.NORTH_DAKOTA_COUNTIES,
    "ohio": counties.OHIO_COUNTIES,
    "oklahoma": counties.OKLAHOMA_COUNTIES,
    "oregon": counties.OREGON_COUNTIES,
    "pennsylvania": counties.PENNSYLVANIA_COUNTIES,
    "rhode island": counties.RHODE_ISLAND_COUNTIES,
    "south carolina": counties.SOUTH_CAROLINA_COUNTIES,
    "south dakota": counties.SOUTH_DAKOTA_COUNTIES,
    "tennessee": counties.TENNESSEE_COUNTIES,
    "texas": counties.TEXAS_COUNTIES,
    "utah": counties.UTAH_COUNTIES,
    "vermont": counties.VERMONT_COUNTIES,
    "virginia": counties.VIRGINIA_COUNTIES,
    "washington": counties.WASHINGTON_COUNTIES,
    "west virginia": counties.WEST_VIRGINIA_COUNTIES,
    "wisconsin": counties.WISCONSIN_COUNTIES,
    "wyoming": counties.WYOMING_COUNTIES,
}

# Initialize Flask app
app = Flask(__name__)


@app.route("/", methods=["GET"])
def dashboard():
    # Renders the HTML UI that users interact with
    clubs = []

    return render_template("dashboard.html", clubs=clubs)


@app.route("/search", methods=["POST"])
def search():
    # Handle POST requests from the frontend search form
    req_data = request.get_json()
    search_term = req_data["term"]
    enriched = []
    if search_term.lower() in state_counties.keys():
        # If a state name is detected, break into counties and search each one
        counties = state_counties.get(search_term.lower())
        location_ids = get_clubs_in_list_of_areas(counties, search_term)
        enriched = enrich_location_list(location_ids, state=search_term)
    else:
        # Otherwise, treat the input as a single city search
        location_ids = get_pickleball_clubs_in_area(search_term)
        enriched = enrich_location_list(location_ids)

    # Save results to disk as a CSV file
    write_locs_as_csv(enriched, req_data["timestamp"])

    # Send enriched list back to frontend as JSON
    results = jsonify(enriched)
    return results


@app.route("/results", methods=["GET"])
def results():
    # Allow client to download the CSV by timestamp-based filename
    return send_file(f"{OUTPUT_DIR}/enriched_{request.args.get('timestamp')}.csv")
