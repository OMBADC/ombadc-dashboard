import csv
import json
import urllib.request
import re
import os

PROJECTS_URL = "https://docs.google.com/spreadsheets/d/1jqUSc8-h7xQtgbK3kNQex9EHjaIusFWDcKJsT78rF3Q/pub?gid=0&single=true&output=csv"
DISTRICTS_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/pub?gid=1237062162&single=true&output=csv"

def fetch_csv(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    response = urllib.request.urlopen(req)
    content = response.read().decode("utf-8")
    return list(csv.DictReader(content.splitlines()))

def fetch_projects():
    rows = fetch_csv(PROJECTS_URL)
    projects = []
    for row in rows:
        try:
            projects.append({
                "id":     int(row["id"]),
                "sector": row["sector"].strip(),
                "name":   row["name"].strip(),
                "dept":   row["dept"].strip(),
                "sanc":   float(row["sanc"] or 0),
                "rel":    float(row["rel"] or 0),
                "exp":    float(row["exp"] or 0),
                "prog":   float(row["prog"] or 0),
                "status": row["status"].strip(),
                "bene":   int(float(row["bene"] or 0)),
            })
        except Exception as e:
            print(f"Skipping row due to error: {e} — row: {row}")
    return projects

def fetch_districts():
    rows = fetch_csv(DISTRICTS_URL)
    districts = []
    for row in rows:
        try:
            districts.append({
                "name":     row["name"].strip(),
                "blocks":   int(row["blocks"] or 0),
                "villages": int(row["villages"] or 0),
                "pop":      int(row["pop"] or 0),
            })
        except Exception as e:
            print(f"Skipping district row: {e} — row: {row}")
    return districts

def inject():
    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()

    projects  = fetch_projects()
    districts = fetch_districts()

    html = html.replace("__PROJECTS_DATA__",  json.dumps(projects,  indent=2))
    html = html.replace("__DISTRICTS_DATA__", json.dumps(districts, indent=2))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Done — {len(projects)} projects, {len(districts)} districts injected.")

if __name__ == "__main__":
    inject()
