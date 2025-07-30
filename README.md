# PickleScraper

**PickleScraper** is a browser-based lead generation tool that helps you find and enrich pickleball club listings using Google’s Places API. It outputs phone numbers, websites, and email contacts into a CSV that you can import into CRMs or outbound platforms. Designed for technical operators and non-engineer builders.

---

## Overview

- Search by **city** or **state**
- Enrich each lead with phone, website, and email

---

## Installation Guide (For Local Development)

### 1. Install Python

Requires **Python 3.10 or newer**.  
Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)

> On Windows, check **"Add Python to PATH"** during installation.

---

### 2. Clone and Set Up the App

#### Windows:

```powershell
git clone https://github.com/your-org/picklescraper.git
cd picklescraper
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
````

#### macOS / Linux:

```bash
git clone https://github.com/your-org/picklescraper.git
cd picklescraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the project root with:

```ini
API_KEY=your_google_places_api_key
SERP_KEY=your_serpapi_key  # optional
OUTPUT_DIR=/absolute/path/to/outputs
```

> ⚠️ `OUTPUT_DIR` must be an **absolute path** and the directory must exist.

---

## Running the App Locally

#### Windows:

```powershell
$env:FLASK_APP = "app.py"
flask run
```

#### macOS / Linux:

```bash
export FLASK_APP=app.py
flask run
```

Navigate to: [http://localhost:5000](http://localhost:5000)

---

## Deployment on PythonAnywhere

PickleScraper is deployed [here](https://operationautopilot.pythonanywhere.com/)

### To deploy or update:

1. **Upload the files** via the PythonAnywhere **Files** tab.
2. **Install requirements** using the PythonAnywhere **Console**:

   ```bash
   pip install -r /home/operationautopilot/oa_webscraper/requirements.txt
   ```
3. **Create the `.env` file** in the same directory with your credentials:

   ```ini
   API_KEY=your_google_places_api_key
   SERP_KEY=your_serpapi_key
   OUTPUT_DIR=/home/operationautopilot/oa_webscraper/output
   ```

   * `OUTPUT_DIR` must be an **absolute path on the PythonAnywhere file system**
   * Make sure the `output` directory exists. You can create it from the menu if need be.
4. Use the **Web tab** to reload your Flask app.

---

## Using the App

1. Input a city or state.
2. Optionally add a ZIP code for more precision.
3. Click **Search**.
4. Wait for results to be fetched and enriched.
5. Click **Download to CSV**.

---

## CSV Output

* Fields:

  * Name
  * Address
  * Phone
  * Website
  * Email (scraped)
* File format: `enriched_<timestamp>.csv`
* Delimiter: `;` (semi-colon)

> Results are saved to disk (`OUTPUT_DIR`), but are **not browsable in the web interface**. Download your CSV immediately or access it manually on disk.

---

## Tech Stack

* **Python 3**
* **Flask** – web interface
* **Google Places API** – location queries
* **Trafilatura** – email scraping
* **dotenv** – environment variable loading

---

## Code Structure

| File               | Purpose                      |
| ------------------ | ---------------------------- |
| `app.py`           | Flask app and routes         |
| `places_api.py`    | Querying + enrichment logic  |
| `enrichment.py`    | Email scraping from websites |
| `counties.py`      | U.S. county reference data   |
| `templates/dashboard.html`    | Actual frontend user interface |
| `requirements.txt` | All Python dependencies      |

---

## Limitations

* CSVs are saved to disk but not viewable from the browser UI
* Email scraping is heuristic — not all entries yield results
* Blacklist filters remove civic or non-commercial venues
* Google API quotas apply based on your usage and key limits

---

## Operational Security (OpSec)

PickleScraper is designed to be used internally or by trusted operators. While it does not store or transmit data beyond Google API calls and optional website fetches for enrichment, you should still follow good opsec practices:

* **Keep your `.env` file private.** Do not commit it to source control. It contains your API keys and should never be shared.
* **Limit access to the server.** If deployed (e.g. on PythonAnywhere), only give access to people you trust with your API quota and output data.
* **Avoid scraping sensitive domains.** The enrichment scraper uses `Trafilatura` to crawl business websites. While it is respectful and lightweight, it is still a crawler. Don’t point it at sites with login portals, sensitive data, or any business where scraping could create legal exposure.
* **Be mindful of data handling.** The CSVs may include scraped emails and phone numbers. Treat that data as PII and handle accordingly — especially if importing into outbound systems.
* **Rotate API keys often**: Especially if handled by many people, the risk of leakage increases. 
---

## Pricing

PickleScraper uses two Google Places API endpoints:

* **Text Search (Essentials)** – `$0.00` per request
  Free when querying for only Place IDs (`X-Goog-FieldMask: places.id`)

* **Place Details (Enterprise)** – `$0.02` per request
  Used to fetch business name, website, phone number, and address

---

### Why Every Result is Enriched

Search results from Google Places API contain only the **Place ID** — no name, no phone, no website, no address.

To evaluate whether a business is valid, PickleScraper needs at least:

* Name (to screen out government/gym/etc)
* Website (to match against domain blacklists)

While it’s technically possible to request individual fields and follow up with another request if a result passes, Google’s billing model charges **per call**, not per field. So making two separate requests (e.g. one to get name, then another for full info) would cost **more** than just fetching everything in one go.

> Result: Every Place ID is enriched with all necessary fields upfront — even if it’s discarded later during filtering.

---

### Cost Per Lead

* Each result enriched costs **\$0.02**, no exceptions
* Final cost per usable lead varies with location and density:

  * **Typical range**: \~\$0.08–\$0.15
  * Higher in regions with low signal or civic-heavy listings

You are billed for everything enriched — not just the results that make it into the CSV.

---

### Estimate Formula for State-Level Queries

Use the following to estimate cost:

```
Total Cost = Y × N × 0.02
```

Where:

* `Y` = number of counties in the state
* `N` = average number of results per county (a safe default is `20`)
* `$0.02` = cost per enrichment call

**Example:**

> A 60-county state with \~20 results per county would cost:
> `60 × 20 × 0.02 = $24.00`
> California roughly matches this description.
---

### Spend Guidelines

| Scope        | Estimated Cost |
| ------------ | -------------- |
| Small states | \$1–\$3        |
| Large states | \$20–\$40      |
| Nationwide   | \$500–600      |

Costs can fluctuate based on regional business density, false positives, and how many results pass your filters.

---

### Recommendations

* **Monitor usage in Google Cloud Console**
* **Set billing alerts or soft limits** before large scans
* **Sample a few counties or cities** before full-state runs

PickleScraper is efficient when used with targeting and awareness — not when left running blind.

