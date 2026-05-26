import json
import sys
import urllib.request
import os

SHEET_ID = "1jqUSc8-h7xQtgbK3kNQex9EHjaIusFWDcKJsT78rF3Q"

PROJECTS_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet=Projects"
DISTRICTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet=Districts"

PROJECT_DISTRICTS = {
    1: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    2: ["Sundargarh"],
    3: ["Sundargarh"],
    4: ["Mayurbhanj"],
    5: ["Mayurbhanj"],
    6: ["Mayurbhanj"],
    7: ["Keonjhar", "Sundargarh", "Jajpur"],
    8: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    9: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    10: ["Jajpur"],
    11: ["Mayurbhanj", "Sundargarh", "Jajpur", "Angul", "Dhenkanal", "Deogarh", "Jharsuguda"],
    12: ["Mayurbhanj", "Sundargarh", "Jajpur", "Angul", "Dhenkanal", "Deogarh", "Jharsuguda"],
    13: ["Mayurbhanj", "Jajpur", "Angul", "Dhenkanal", "Deogarh", "Jharsuguda"],
    14: ["Mayurbhanj", "Sundargarh", "Jajpur", "Jharsuguda"],
    15: ["Mayurbhanj", "Sundargarh", "Jajpur"],
    16: ["Jajpur"],
    17: ["Jajpur"],
    18: ["Keonjhar", "Mayurbhanj", "Sundargarh"],
    19: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    20: ["Mayurbhanj"],
    21: ["Mayurbhanj"],
    22: ["Keonjhar"],
    23: ["Mayurbhanj"],
    24: ["Sundargarh"],
    25: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Angul", "Deogarh", "Jharsuguda"],
    26: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Angul", "Dhenkanal", "Deogarh", "Jharsuguda"],
    27: ["Jharsuguda"],
    28: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Angul", "Dhenkanal", "Deogarh", "Jharsuguda"],
    29: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Dhenkanal", "Deogarh", "Jharsuguda"],
    30: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Jharsuguda"],
    31: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    32: ["Jajpur"],
    33: ["Mayurbhanj"],
    34: ["Mayurbhanj"],
    35: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Deogarh"],
    36: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Angul", "Dhenkanal", "Deogarh", "Jharsuguda"],
    37: ["Jajpur"],
    38: ["Keonjhar", "Mayurbhanj", "Sundargarh"],
    39: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Dhenkanal", "Deogarh", "Jharsuguda"],
    40: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Dhenkanal", "Deogarh", "Jharsuguda"],
    41: ["Keonjhar", "Sundargarh", "Deogarh"],
    42: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    43: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    44: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    45: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    46: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    47: ["Keonjhar", "Mayurbhanj", "Jajpur"],
    48: ["Jajpur"],
    49: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    50: ["Sundargarh"],
    51: ["Keonjhar"],
    52: ["Angul"],
    53: ["Mayurbhanj"],
    54: ["Angul"],
    55: ["Keonjhar", "Mayurbhanj", "Sundargarh"],
    56: ["Keonjhar", "Sundargarh"],
    57: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur"],
    58: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Deogarh", "Jharsuguda"],
    59: ["Keonjhar", "Mayurbhanj", "Sundargarh", "Jajpur", "Dhenkanal", "Deogarh", "Jharsuguda"],
    60: ["Keonjhar", "Mayurbhanj", "Sundargarh"]
}

def fetch_sheet_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read().decode("utf-8")
    start = raw.index("{")
    end   = raw.rindex("}") + 1
    return json.loads(raw[start:end])

def parse_rows(data):
    cols = []
    for c in data["table"]["cols"]:
        label = c.get("label", "").strip() or c.get("id", "").strip()
        cols.append(label)
    rows = []
    for row in data["table"]["rows"]:
        if row is None: continue
        record = {}
        for i, cell in enumerate(row["c"]):
            if i < len(cols):
                record[cols[i]] = cell["v"] if cell and cell.get("v") is not None else ""
        rows.append(record)
    return rows

def fetch_projects():
    data = fetch_sheet_json(PROJECTS_URL)
    rows = parse_rows(data)
    projects = []
    for i, row in enumerate(rows):
        p_id = int(float(str(row.get("id", i+1))))
        projects.append({
            "id":        p_id,
            "sector":    str(row.get("sector", "")).strip(),
            "name":      str(row.get("name",   "")).strip(),
            "dept":      str(row.get("dept",   "")).strip(),
            "sanc":      float(str(row.get("sanc", 0)) or 0),
            "rel":       float(str(row.get("rel",  0)) or 0),
            "exp":       float(str(row.get("exp",  0)) or 0),
            "prog":      float(str(row.get("prog", 0)) or 0),
            "status":    str(row.get("status", "Ongoing")).strip(),
            "bene":      int(float(str(row.get("bene", 0)) or 0)),
            "districts": PROJECT_DISTRICTS.get(p_id, [])
        })
    return projects

def fetch_districts():
    data = fetch_sheet_json(DISTRICTS_URL)
    rows = parse_rows(data)
    districts = []
    for row in rows:
        districts.append({
            "name":     str(row.get("name", "")).strip(),
            "blocks":   int(float(str(row.get("blocks", 0)) or 0)),
            "villages": int(float(str(row.get("villages", 0)) or 0)),
            "pop":      int(float(str(row.get("pop", 0)) or 0)),
        })
    return districts

def inject():
    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()

    projects  = fetch_projects()
    districts = fetch_districts()

    # Load SVG Map
    if os.path.exists("odisha_map.svg"):
        with open("odisha_map.svg", "r") as f:
            svg_content = f.read()
            html = html.replace("__MAP_SVG__", svg_content)
    else:
        html = html.replace("__MAP_SVG__", "<p>Map Error</p>")

    html = html.replace("__PROJECTS_DATA__",  json.dumps(projects,  indent=2))
    html = html.replace("__DISTRICTS_DATA__", json.dumps(districts, indent=2))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("SUCCESS: index.html updated with redesign")

if __name__ == "__main__":
    inject()
