from flask import Flask, render_template, request, jsonify, send_file
from oa_webscraper.places_api import (
    get_pickleball_clubs_in_area,
    enrich_location_list,
    write_locs_as_csv,
)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def dashboard():
    clubs = []

    return render_template("dashboard.html", clubs=clubs)


@app.route("/search", methods=["POST"])
def search():
    req_data = request.get_json()
    print(req_data)
    search_term = req_data["term"]
    location_ids = get_pickleball_clubs_in_area(search_term)
    enriched = enrich_location_list(location_ids)
    write_locs_as_csv(enriched, req_data["timestamp"])

    results = jsonify(enriched)
    return results


@app.route("/results", methods=["GET"])
def results():
    return send_file(f"enriched_{request.args.get('timestamp')}.csv")
