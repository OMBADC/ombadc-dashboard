import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        file_path = os.path.abspath('index.html')
        await page.goto(f'file://{file_path}')

        # Screenshot of Landing Page
        await page.screenshot(path='screenshot_landing.png', full_page=True)

        # Click "Access Analytics Center"
        await page.click('button:has-text("Access Analytics Center")')
        await asyncio.sleep(1) # Wait for transition

        # Screenshot of Dashboard
        await page.screenshot(path='screenshot_dashboard.png', full_page=True)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
