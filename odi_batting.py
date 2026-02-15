import asyncio
import csv
from playwright.async_api import async_playwright

async def scrape_and_clean_data():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Go to the desired URL
        await page.goto("https://stats.espncricinfo.com/ci/engine/stats/index.html?class=2;spanmax1=31+Dec+2015;spanmin1=01+Jan+2015;spanval1=span;team=6;template=results;type=batting")
        
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
                cells.append("2015")
                player_data.append(cells)

        # Close the browser
        await browser.close()

    # Add appropriate headers
    headers = ["Player Name", "Matches", "Innings", "Not Outs", "Runs", "High Score", "Average",
               "Balls Faced", "Strike Rate", "100s", "50s", "Ducks", "4s", "6s", "Year"]
    
    # Write the player data to a CSV file
    with open('odi_batting_2015.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the header row
        writer.writerows(player_data)  # Write the data rows

    print("Data saved to 'odi_batting_2015.csv'.")

# Run the async function
asyncio.run(scrape_and_clean_data())
