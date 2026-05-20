import os
from playwright.sync_api import sync_playwright

def verify_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        file_path = "file://" + os.path.abspath("index.html")
        print(f"Navigating to {file_path}")
        page.goto(file_path)
        page.wait_for_timeout(1000)

        # 1. Landing
        page.screenshot(path="v6_landing.png")

        # 2. Enter Dashboard
        page.click("text=Access Analytics Center")
        page.wait_for_timeout(1000)
        page.screenshot(path="v6_dashboard.png")

        # 3. Filter by Keonjhar (Path index 4)
        # Using selector for paths in map-container
        paths = page.query_selector_all("#map-container path")
        print(f"Found {len(paths)} paths")
        if len(paths) > 4:
            paths[4].click()
            page.wait_for_timeout(1000)
            page.screenshot(path="v6_filtered.png")

        # 4. District Watch
        page.click("text=District Watch")
        page.wait_for_timeout(1000)
        page.screenshot(path="v6_districts.png")

        # 5. Project Pipeline
        page.click("text=Project Pipeline")
        page.wait_for_timeout(1000)
        page.screenshot(path="v6_projects.png")

        # 6. Fund Flows
        page.click("text=Fund Flows")
        page.wait_for_timeout(1000)
        page.screenshot(path="v6_financials.png")

        browser.close()

if __name__ == "__main__":
    verify_dashboard()
