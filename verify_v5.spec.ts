import { test, expect } from '@playwright/test';
import path from 'path';

test('Verify full dashboard redesign', async ({ page }) => {
    const filePath = 'file://' + path.resolve('index.html');
    await page.goto(filePath);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'v5_landing.png' });

    // Enter Dashboard
    await page.click('button:has-text("Access Analytics Center")');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'v5_command_center.png' });

    // Filter by Keonjhar (Index 4)
    const paths = await page.$$('.map-district');
    // Keonjhar is index 4 according to my previous mapping
    await paths[4].click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'v5_command_center_filtered.png' });

    // Switch to District Watch
    await page.click('button:has-text("District Watch")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'v5_district_watch.png' });

    // Switch to Project Pipeline
    await page.click('button:has-text("Project Pipeline")');
    await page.waitForTimeout(500);
    await page.fill('#project-search', 'Mega');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'v5_project_pipeline.png' });

    // Switch to Fund Flows
    await page.click('button:has-text("Fund Flows")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'v5_fund_flows.png' });
});
