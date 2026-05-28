"""
inject_data.py — OMBADC Dashboard Data Injector
Fetches Projects, Districts, and Map tabs from Google Sheets,
then injects them into template.html → index.html
"""

import json
import re
import urllib.request
import urllib.error
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────────────
SHEET_ID = "1jqUSc8-h7xQtgbK3kNQex9EHjaIusFWDcKJsT78rF3Q"

SHEET_GIDS = {
    "Projects":  "0",
    "Districts": "1237062162",
    "Map":       "1333287805",
}

TEMPLATE_FILE = "template.html"
OUTPUT_FILE   = "index.html"

# ── HELPERS ────────────────────────────────────────────────────────────────

def sheet_url(gid):
    return (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:json&gid={gid}"
    )


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
        for i, cell in enumerate(row.get("c", [])):
            if i < len(cols):
                record[cols[i]] = cell["v"] if cell and cell.get("v") is not None else ""
        rows.append(record)
    print(f"  First row sample: {rows[0] if rows else 'NO ROWS'}")
    return rows


def safe_float(val, default=0.0):
    """Convert a value to float safely."""
    if val is None or val == "":
        return default
    try:
        # Remove commas and % signs
        return float(str(val).replace(",", "").replace("%", "").strip())
    except (ValueError, TypeError):
        return default


def safe_str(val):
    """Convert to string, strip whitespace, replace literal newlines."""
    return str(val).replace("\n", " ").replace("\r", " ").strip() if val is not None else ""


# ── FETCH PROJECTS ─────────────────────────────────────────────────────────

def fetch_projects():
    """
    Projects tab columns:
    id, sector, name, dept, sanc, rel, exp, prog, status, bene
    """
    print("\n[Projects tab]")
    data = fetch_sheet_json(sheet_url(SHEET_GIDS["Projects"]))
    raw_rows = parse_rows(data)

    projects = []
    for row in raw_rows:
        # Skip completely empty rows
        if not any(str(v).strip() for v in row.values()):
            continue
        proj = {
            "id":     int(safe_float(row.get("id", 0))),
            "sector": safe_str(row.get("sector", "")),
            "name":   safe_str(row.get("name", "")),
            "dept":   safe_str(row.get("dept", "")),
            "sanc":   safe_float(row.get("sanc", 0)),
            "rel":    safe_float(row.get("rel", 0)),
            "exp":    safe_float(row.get("exp", 0)),
            "prog":   safe_float(row.get("prog", 0)),
            "status": safe_str(row.get("status", "Ongoing")),
            "bene":   safe_float(row.get("bene", 0)),
        }
        if proj["name"]:
            projects.append(proj)

    print(f"  → {len(projects)} projects loaded")
    return projects


# ── FETCH DISTRICTS ────────────────────────────────────────────────────────

def fetch_districts():
    """
    Districts tab columns: name, blocks, villages, pop
    """
    print("\n[Districts tab]")
    data = fetch_sheet_json(sheet_url(SHEET_GIDS["Districts"]))
    raw_rows = parse_rows(data)

    districts = []
    for row in raw_rows:
        if not any(str(v).strip() for v in row.values()):
            continue
        dist = {
            "name":     safe_str(row.get("name", "")),
            "blocks":   int(safe_float(row.get("blocks", 0))),
            "villages": int(safe_float(row.get("villages", 0))),
            "pop":      int(safe_float(row.get("pop", 0))),
        }
        if dist["name"]:
            districts.append(dist)

    print(f"  → {len(districts)} districts loaded")
    return districts


# ── FETCH MAP DATA ─────────────────────────────────────────────────────────

def fetch_map():
    """
    Map tab columns:
    Sl_No, Project_Name, Sector, Approved_Cost_Cr, Board_Approval_Date,
    Line_Department, Executing_Agency, Sanctioned_Cost_Cr,
    Execution_Period, Districts, Physical_Progress_Pct, Financial_Progress_Pct

    Output: dict keyed by district name, value = list of project dicts
    One project can appear under multiple districts (semicolon-separated).
    """
    print("\n[Map tab]")
    data = fetch_sheet_json(sheet_url(SHEET_GIDS["Map"]))
    raw_rows = parse_rows(data)

    # Build district → [projects] index
    map_data = {}

    for row in raw_rows:
        if not any(str(v).strip() for v in row.values()):
            continue

        districts_raw = safe_str(row.get("Districts", ""))
        if not districts_raw:
            continue

        # Split semicolon-separated district names
        district_names = [d.strip() for d in districts_raw.split(";") if d.strip()]

        proj = {
            "sl":                   int(safe_float(row.get("Sl_No", 0))),
            "name":                 safe_str(row.get("Project_Name", "")),
            "sector":               safe_str(row.get("Sector", "")),
            "approved_cost":        safe_float(row.get("Approved_Cost_Cr", 0)),
            "approval_date":        safe_str(row.get("Board_Approval_Date", "")),
            "line_dept":            safe_str(row.get("Line_Department", "")),
            "executing_agency":     safe_str(row.get("Executing_Agency", "")),
            "sanctioned_cost":      safe_float(row.get("Sanctioned_Cost_Cr", 0)),
            "execution_period":     safe_str(row.get("Execution_Period", "")),
            "districts":            districts_raw,
            "physical_pct":         safe_float(row.get("Physical_Progress_Pct", 0)),
            "financial_pct":        safe_float(row.get("Financial_Progress_Pct", 0)),
        }

        if not proj["name"]:
            continue

        for dist_name in district_names:
            if dist_name not in map_data:
                map_data[dist_name] = []
            map_data[dist_name].append(proj)

    total_projects = sum(len(v) for v in map_data.values())
    print(f"  → {len(map_data)} districts, {total_projects} project-district entries")
    for k, v in sorted(map_data.items()):
        print(f"     {k}: {len(v)} projects")
    return map_data


# ── INJECT INTO TEMPLATE ───────────────────────────────────────────────────

def build_index(projects, districts, map_data):
    print(f"\n[Building {OUTPUT_FILE}]")

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Serialise to JSON (compact, no trailing whitespace in strings)
    projects_json  = json.dumps(projects,  ensure_ascii=False, separators=(",", ":"))
    districts_json = json.dumps(districts, ensure_ascii=False, separators=(",", ":"))
    map_json       = json.dumps(map_data,  ensure_ascii=False, separators=(",", ":"))

    # Sanity: no literal newlines inside the JSON strings
    for label, s in [("projects", projects_json), ("districts", districts_json), ("map", map_json)]:
        if "\n" in s:
            raise ValueError(f"Literal newline found in {label} JSON — aborting")

    html = html.replace("__PROJECTS_DATA__",  projects_json)
    html = html.replace("__DISTRICTS_DATA__", districts_json)
    html = html.replace("__MAP_DATA__",       map_json)

    # Verify all placeholders replaced
    for ph in ["__PROJECTS_DATA__", "__DISTRICTS_DATA__", "__MAP_DATA__"]:
        if ph in html:
            raise ValueError(f"Placeholder {ph} not replaced — check template")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  → Written {len(html):,} chars to {OUTPUT_FILE}")


# ── MAIN ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"OMBADC Dashboard — Data Injection")
    print(f"Run time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    projects  = fetch_projects()
    districts = fetch_districts()
    map_data  = fetch_map()

    build_index(projects, districts, map_data)

    print("\n✓ Done — index.html is ready.")
