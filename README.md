# PickleScraper

**PickleScraper** is a browser-based lead generation tool that helps you find and enrich pickleball club listings using Google’s Places API. It outputs phone numbers, websites, and email contacts into a CSV that you can import into CRMs or outbound platforms. Designed for technical operators and non-engineer builders.

---

## Overview

- Search by **city** or **state**
- Enrich each lead with phone, website, and email
- Avoids false positives using smart filters
- Output is a **CRM-ready CSV**
- Works via browser, no coding required

---

## Installation Guide (Local)

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

PickleScraper is deployed at [https://yourusername.pythonanywhere.com](https://yourusername.pythonanywhere.com)

### To deploy or update:

1. **Upload the files** via the PythonAnywhere **Files** tab.
2. **Install requirements** using the PythonAnywhere **Console**:

   ```bash
   pip install -r /home/yourusername/picklescraper/requirements.txt
   ```
3. **Create the `.env` file** in the same directory with your credentials:

   ```ini
   API_KEY=your_google_places_api_key
   SERP_KEY=your_serpapi_key
   OUTPUT_DIR=/home/yourusername/picklescraper/outputs
   ```

   * `OUTPUT_DIR` must be an **absolute path on the PythonAnywhere file system**
   * Make sure the `/outputs` directory exists
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
| `requirements.txt` | All Python dependencies      |

---

## Limitations

* CSVs are saved to disk but not viewable from the browser UI
* Email scraping is heuristic — not all entries yield results
* Blacklist filters remove civic or non-commercial venues
* Google API quotas apply based on your usage and key limits

* Absolutely — here’s the raw content you can add to the README, covering both **operational security (opsec)** and **cost/pricing realities**, with clear and direct language tailored for internal users or operators.

---

## Operational Security (OpSec)

PickleScraper is designed to be used internally or by trusted operators. While it does not store or transmit data beyond Google API calls and optional website fetches for enrichment, you should still follow good opsec practices:

* **Keep your `.env` file private.** Do not commit it to source control. It contains your API keys and should never be shared.
* **Limit access to the server.** If deployed (e.g. on PythonAnywhere), only give access to people you trust with your API quota and output data.
* **Avoid scraping sensitive domains.** The enrichment scraper uses `Trafilatura` to crawl business websites. While it is respectful and lightweight, it is still a crawler. Don’t point it at sites with login portals, sensitive data, or any business where scraping could create legal exposure.
* **Be mindful of data handling.** The CSVs may include scraped emails and phone numbers. Treat that data as PII and handle accordingly — especially if importing into outbound systems.
* **Rotate API keys often**: Especially if handled by many people, the risk of leakage increases. 
---

## Pricing & API Usage

Absolutely — here’s the final, polished **Pricing** section with a suggested sample average (`N = 20`) included in the formula explanation to help non-technical users make quick estimates:

---

## Pricing

PickleScraper uses two endpoints from the Google Places API:

* **Text Search (Essentials)** – `$0.00` per request
  (Free when only requesting `places.id` via `X-Goog-FieldMask`)

* **Place Details (Enterprise)** – `$0.02` per request
  (Used to fetch business details like name, phone, website, and address)

### How Billing Works

Each search returns only a list of Place IDs — not usable data.

To determine whether a business is relevant, PickleScraper needs fields like:

* Business name
* Website URL
* Phone number
* Address

Rather than making multiple paid calls to fetch these fields individually, PickleScraper makes a **single Place Details (Enterprise)** request per result to retrieve everything needed for filtering. This approach:

* Minimizes total requests
* Keeps enrichment logic simple
* Ensures all filtering happens with full context

> You are charged `$0.02` for **every Place ID returned**, even if the business is later discarded during filtering. Text search is free; enrichment is not.

---

### Cost Per Lead

* Typical cost per usable lead: **\$0.08–\$0.15**
* You pay for all enrichments — not just the ones that survive filtering
* Low-yield areas (e.g. rural or civic-heavy regions) will increase cost per usable lead

---

### Typical Spend

* Small states: **\$1–\$3**
* Large states: **\$10–\$50**
* Nationwide: **\$500–600**

Actual cost varies based on:

* The number of counties in the state
* How many Place IDs are returned across all search queries
* How strict your filters are (which don’t affect cost, only output)

---

### Estimate Formula for Any State

To estimate the cost of scraping a specific state:

```
Total Cost = Y × N × 0.02
```

Where:

* `Y` = number of counties in the state
* `N` = average number of Place results returned per county
* `$0.02` = cost per Place Details (Enterprise) request

**Sample Average:**
If you don’t have data yet, use `N = 20` as a conservative default — this assumes that across three search queries per county, you’ll get around 20 unique places that trigger enrichment.

**Example:**

```
State with 60 counties
Estimated cost = 60 × 20 × 0.02 = $24.00
```

This provides a quick way to budget based on state size.

---
