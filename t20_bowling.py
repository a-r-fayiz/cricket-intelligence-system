import asyncio
import csv
from playwright.async_api import async_playwright

async def scrape_and_clean_data():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Loop through the years 2015 to 2024
        for year in range(2015, 2025):
            print(f"Processing data for the year {year}...")

            # Construct the URL for the given year
            url = (
                f"https://stats.espncricinfo.com/ci/engine/stats/index.html?"
                f"class=3;spanmax1=31+Dec+{year};spanmin1=01+Jan+{year};spanval1=span;"
                f"team=6;template=results;type=bowling"
            )

            # Go to the URL
            await page.goto(url)
            
            # Wait for the table to load
            await page.wait_for_selector("table")

            # Extract the rows with the class 'data1' which contain player data
            rows = await page.locator("tr.data1").all()

            player_data = []
            
            # Process each row
            for row in rows:
                # Extract cell values and strip whitespace
                cells = [cell.strip() for cell in await row.locator("td").all_inner_texts()]
                
                # Remove empty cells
                cells = [cell for cell in cells if cell]
                
                # Add the Year column dynamically to each row of player data
                if cells:  # Ensure non-empty rows are processed
                    cells.append(str(year))
                    player_data.append(cells)

            # Update the headers for the bowling table
            headers = [
                "Player Name", "Matches", "Innings", "Overs", "Maidens", "Runs", "Wickets", 
                "BBI", "Average", "Economy Rate", "Strike Rate", "4 Wicket Hauls", 
                "5 Wicket Hauls", "Year"
            ]
            
            # Write the player data to a CSV file named after the year
            file_name = f't20_bowling_{year}.csv'
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)  # Write the header row
                writer.writerows(player_data)  # Write the data rows

            print(f"Data for the year {year} saved to '{file_name}'.")

        # Close the browser
        await browser.close()

# Run the async function
asyncio.run(scrape_and_clean_data())
