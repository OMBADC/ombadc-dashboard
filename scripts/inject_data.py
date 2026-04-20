import json
import sys
import urllib.request

SHEET_ID = "1jqUSc8-h7xQtgbK3kNQex9EHjaIusFWDcKJsT78rF3Q"

PROJECTS_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet=Projects"
DISTRICTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet=Districts"

def fetch_sheet_json(url):
    print(f"  Fetching: {url[:80]}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read().decode("utf-8")
    print(f"  Response length: {len(raw)} chars")
    print(f"  First 500 chars: {raw[:500]}")
    start = raw.index("{")
    end   = raw.rindex("}") + 1
    data  = json.loads(raw[start:end])
    return data

def parse_rows(data):
    print(f"  Raw cols: {data['table']['cols'][:5]}")
    cols = []
    for c in data["table"]["cols"]:
        label = c.get("label", "").strip()
        if not label:
            label = c.get("id", "").strip()
        cols.append(label)
    print(f"  Columns parsed: {cols}")
    rows = []
    for row in data["table"]["rows"]:
        if row is None:
            continue
        record = {}
        for i, cell in enumerate(row["c"]):
            if i < len(cols):
                record[cols[i]] = cell["v"] if cell and cell.get("v") is not None else ""
        rows.append(record)
    print(f"  First row sample: {rows[0] if rows else 'NO ROWS'}")
    return rows

def fetch_projects():
    print("Fetching Projects sheet...")
    data = fetch_sheet_json(PROJECTS_URL)
    rows = parse_rows(data)
    print(f"  Found {len(rows)} rows")
    projects = []
    for i, row in enumerate(rows):
        try:
            projects.append({
                "id":     int(float(str(row.get("id",     i+1)))),
                "sector": str(row.get("sector", "")).strip(),
                "name":   str(row.get("name",   "")).strip(),
                "dept":   str(row.get("dept",   "")).strip(),
                "sanc":   float(str(row.get("sanc", 0)) or 0),
                "rel":    float(str(row.get("rel",  0)) or 0),
                "exp":    float(str(row.get("exp",  0)) or 0),
                "prog":   float(str(row.get("prog", 0)) or 0),
                "status": str(row.get("status", "Ongoing")).strip(),
                "bene":   int(float(str(row.get("bene", 0)) or 0)),
            })
        except Exception as e:
            print(f"  Warning: skipping row {i+2}: {e} — {row}")
    print(f"  Parsed {len(projects)} projects successfully")
    return projects

def fetch_districts():
    print("Fetching Districts sheet...")
    data = fetch_sheet_json(DISTRICTS_URL)
    rows = parse_rows(data)
    print(f"  Found {len(rows)} rows")
    districts = []
    for i, row in enumerate(rows):
        try:
            districts.append({
                "name":     str(row.get("name",     "")).strip(),
                "blocks":   int(float(str(row.get("blocks",   0)) or 0)),
                "villages": int(float(str(row.get("villages", 0)) or 0)),
                "pop":      int(float(str(row.get("pop",      0)) or 0)),
            })
        except Exception as e:
            print(f"  Warning: skipping district row {i+2}: {e} — {row}")
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

    if not projects:
        print("ERROR: No projects parsed — aborting")
        sys.exit(1)

    if not districts:
        print("ERROR: No districts parsed — aborting")
        sys.exit(1)

    html = html.replace("__PROJECTS_DATA__",  json.dumps(projects,  indent=2))
    html = html.replace("__DISTRICTS_DATA__", json.dumps(districts, indent=2))

    print("Writing index.html...")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"SUCCESS — {len(projects)} projects and {len(districts)} districts written to index.html")

if __name__ == "__main__":
    inject()
