#This is broken!
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

def scrape_ebitda_listings_final():
    """
    Automates a browser to click 'Start Search', then 'All', 
    and scrapes all results from the fully loaded page.
    """
    # Set up the Chrome driver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Start at the main page, not the search results page
    start_url = "https://ebitdabusinessadvisors.com/businesses-for-sale/"
    driver.get(start_url)
    
    listings = []
    print("✅ Browser opened, navigating to the website...")

    try:
        # STEP 1: Wait for and click the "Start Search" button
        print("⏳ Waiting for and clicking 'Start Search'...")
        start_search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Start Search' and @class='special2']"))
        )
        start_search_button.click()

        # STEP 2: Wait for the results page and click the "All" button
        print("⏳ Waiting for and clicking the 'All' button to display all listings...")
        all_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='All' and @name='displayall']"))
        )
        all_button.click()

        # STEP 3: Wait for the final page with all listings to load
        print("⏳ Waiting for all listings to load on the page...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wpas-result-content"))
        )
        # Add a small buffer just to ensure everything has rendered
        time.sleep(3)

        # STEP 4: Scrape the data from the fully loaded page
        print("⚙️ All listings loaded. Now scraping the data...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listing_cards = soup.find_all('div', class_='wpas-result-content')

        print(f"👍 Found {len(listing_cards)} total listings to scrape.")

        for card in listing_cards:
            # The parsing logic remains the same
            header = card.find('h3')
            name = header.get_text(strip=True) if header else 'N/A'
            listing_url = header.find_parent('a')['href'] if header else 'N/A'
            
            details = {'Location': 'N/A', 'Price': 'N/A', 'Down Payment': 'N/A', 'Listing Number': 'N/A', 'Discretionary Earnings': 'N/A', 'Sales Revenue': 'N/A'}
            meta_items = card.find('ul', class_='wpas-result-meta').find_all('li')
            for item in meta_items:
                text = item.get_text(strip=True)
                if 'Location:' in text:
                    details['Location'] = text.replace('Location:', '').strip()
                elif 'Asking Price:' in text:
                    details['Price'] = text.replace('Asking Price:', '').strip()
                elif 'Down Payment:' in text:
                    details['Down Payment'] = text.replace('Down Payment:', '').strip()
                elif 'Listing Number:' in text:
                    details['Listing Number'] = text.replace('Listing Number:', '').strip()
                elif 'Cash Flow:' in text:
                    details['Discretionary Earnings'] = text.replace('Cash Flow:', '').strip()
                elif 'Gross Revenue:' in text:
                    details['Sales Revenue'] = text.replace('Gross Revenue:', '').strip()
            
            notes_p = card.find('p')
            notes = notes_p.get_text(strip=True) if notes_p else 'N/A'

            listings.append({'Name': name, 'Location': details['Location'], 'Price': details['Price'], 'Down Payment': details['Down Payment'], 'Listing Number': details['Listing Number'], 'Discretionary Earnings': details['Discretionary Earnings'], 'Sales Revenue': details['Sales Revenue'], 'Notes/Details': notes, 'URL': listing_url})

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit() # Always close the browser

    # STEP 5: Save the data to Excel
    if not listings:
        print("❌ Scraping finished, but no data was collected. Please double-check the button selectors or website structure.")
        return

    df = pd.DataFrame(listings)
    df.to_excel('ebitda_listings.xlsx', index=False)
    print(f"\n🎉 Success! Scraped {len(listings)} listings and saved them to ebitda_listings.xlsx")

if __name__ == '__main__':
    scrape_ebitda_listings_final()