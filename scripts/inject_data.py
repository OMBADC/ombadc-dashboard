import csv
import json
import io
import sys
import requests

PROJECTS_URL  = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/pub?gid=0&single=true&output=csv"
DISTRICTS_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/pub?gid=YOUR_DISTRICTS_GID&single=true&output=csv"

def fetch_csv(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, allow_redirects=True, timeout=30)
    print(f"  Status code: {response.status_code} for {url[:60]}...")
    response.raise_for_status()
    content = response.content.decode("utf-8-sig")  # handles BOM if present
    return list(csv.DictReader(io.StringIO(content)))

def fetch_projects():
    print("Fetching projects...")
    rows = fetch_csv(PROJECTS_URL)
    print(f"  Found {len(rows)} rows")
    projects = []
    for i, row in enumerate(rows):
        try:
            projects.append({
                "id":     int(float(row["id"])),
                "sector": row["sector"].strip(),
                "name":   row["name"].strip(),
                "dept":   row["dept"].strip(),
                "sanc":   float(row["sanc"] or 0),
                "rel":    float(row["rel"]  or 0),
                "exp":    float(row["exp"]  or 0),
                "prog":   float(row["prog"] or 0),
                "status": row["status"].strip(),
                "bene":   int(float(row["bene"] or 0)),
            })
        except Exception as e:
            print(f"  Warning: skipping row {i+2}: {e} — {dict(row)}")
    print(f"  Parsed {len(projects)} projects successfully")
    return projects

def fetch_districts():
    print("Fetching districts...")
    rows = fetch_csv(DISTRICTS_URL)
    print(f"  Found {len(rows)} rows")
    districts = []
    for i, row in enumerate(rows):
        try:
            districts.append({
                "name":     row["name"].strip(),
                "blocks":   int(float(row["blocks"]   or 0)),
                "villages": int(float(row["villages"] or 0)),
                "pop":      int(float(row["pop"]      or 0)),
            })
        except Exception as e:
            print(f"  Warning: skipping district row {i+2}: {e} — {dict(row)}")
    print(f"  Parsed {len(districts)} districts successfully")
    return districts

def inject():
    print("Reading template.html...")
    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()

    if "__PROJECTS_DATA__" not in html:
        print("ERROR: __PROJECTS_DATA__ placeholder not found in template.html")
        sys.exit(1)

    if "__DISTRICTS_DATA__" not in html:
        print("ERROR: __DISTRICTS_DATA__ placeholder not found in template.html")
        sys.exit(1)

    projects  = fetch_projects()
    districts = fetch_districts()

    html = html.replace("__PROJECTS_DATA__",  json.dumps(projects,  indent=2))
    html = html.replace("__DISTRICTS_DATA__", json.dumps(districts, indent=2))

    print("Writing index.html...")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Done — {len(projects)} projects and {len(districts)} districts injected into index.html")

if __name__ == "__main__":
    inject()
