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
