import asyncio
import csv
import os
from playwright.async_api import async_playwright, TimeoutError

BASE_URL = "https://stats.espncricinfo.com/ci/engine/stats/index.html"

FORMATS = {"test": 1, "odi": 2, "t20": 3}
TYPES = ["batting", "bowling"]
TEAM_ID = 6
YEARS = range(2011, 2026)

OUTPUT_DIR = "cricket_stats"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Limit concurrency to avoid Cricinfo blocking
sem = asyncio.Semaphore(2)

# Correct headers per format & type
headers = {
    "test": {
        "batting": ["Player Name", "Matches", "Innings", "Not Outs", "Runs", "High Score", "Average",
                    "Balls Faced", "Strike Rate", "100s", "50s", "Ducks", "4s", "6s", "Year"],

        "bowling": ["Player Name", "Matches", "Innings", "Overs", "Maidens", "Runs", "Wickets",
                    "BBI", "BBM", "Average", "Economy Rate", "Strike Rate",
                    "5 Wicket Hauls", "10 Wicket Hauls", "Year"]
    },

    "odi": {
        "batting": ["Player Name", "Matches", "Innings", "Not Outs", "Runs", "High Score", "Average",
                    "Balls Faced", "Strike Rate", "100s", "50s", "Ducks", "4s", "6s", "Year"],

        "bowling": ["Player Name", "Matches", "Innings", "Overs", "Maidens", "Runs", "Wickets",
                    "BBI", "Average", "Economy Rate", "Strike Rate",
                    "4 Wicket Hauls", "5 Wicket Hauls", "Year"]
    },

    "t20": {
        "batting": ["Player Name", "Matches", "Innings", "Not Outs", "Runs", "High Score", "Average",
                    "Balls Faced", "Strike Rate", "100s", "50s", "Ducks", "4s", "6s", "Year"],

        "bowling": ["Player Name", "Matches", "Innings", "Overs", "Maidens", "Runs", "Wickets",
                    "BBI", "Average", "Economy Rate", "Strike Rate",
                    "4 Wicket Hauls", "5 Wicket Hauls", "Year"]
    }
}


async def scrape_data(format_name, format_id, stat_type):
    async with sem:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Increase timeout
            page.set_default_timeout(120000)
            page.set_default_navigation_timeout(120000)

            for year in YEARS:
                url = (
                    f"{BASE_URL}?class={format_id};"
                    f"spanmax1=31+Dec+{year};spanmin1=01+Jan+{year};"
                    f"spanval1=span;team={TEAM_ID};"
                    f"template=results;type={stat_type}"
                )

                print(f"Scraping: {format_name.upper()} | {stat_type.upper()} | {year}")

                success = False
                for attempt in range(3):
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=120000)
                        await page.wait_for_selector("table", timeout=120000)
                        success = True
                        break
                    except TimeoutError:
                        print(f"⚠ Timeout: {url} (Attempt {attempt+1}/3)")
                        await asyncio.sleep(5)

                if not success:
                    print(f"❌ Skipping {format_name} {stat_type} {year}")
                    continue

                rows = await page.locator("tr.data1").all()
                player_data = []

                expected_cols = len(headers[format_name][stat_type]) - 1  # without Year

                for row in rows:
                    cells = [cell.strip() for cell in await row.locator("td").all_inner_texts()]
                    cells = [cell for cell in cells if cell]

                    if not cells:
                        continue

                    # Fix column shifting issue
                    if len(cells) >= expected_cols:
                        cells = cells[:expected_cols]  # Trim extra
                    else:
                        continue  # Skip broken rows

                    cells.append(str(year))
                    player_data.append(cells)

                file_name = f"{format_name}_{stat_type}_{year}.csv"
                file_path = os.path.join(OUTPUT_DIR, file_name)

                with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(headers[format_name][stat_type])
                    writer.writerows(player_data)

                print(f"✅ Saved: {file_path}")

                await asyncio.sleep(1)

            await browser.close()


async def main():
    tasks = []

    for format_name, format_id in FORMATS.items():
        for stat_type in TYPES:
            tasks.append(scrape_data(format_name, format_id, stat_type))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
