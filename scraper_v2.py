import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class StrollerTableScraper:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Commented out to show browser window
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_table(self, url):
        self.driver.get(url)
        print("\nPlease log in to Consumer Reports in the Chrome window that opened.")
        print("Waiting 30 seconds for you to log in...")
        time.sleep(30)  # Wait for manual login
        
        try:
            # Wait for product rows to be present
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'row-product'))
            )
            time.sleep(10)  # Increased wait time to ensure dynamic content is fully loaded
        except Exception as e:
            print(f"Error waiting for product rows: {e}")
            return []
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        strollers = []
        
        # Find all product rows
        product_rows = soup.find_all('div', class_='row-product')
        
        for row in product_rows:
            stroller_data = {}
            
            # Get product name
            product_name = row.find('a', class_='product__info-display')
            if product_name:
                stroller_data['Product Name'] = product_name.get_text().strip()
            
            # Get overall score
            score_blob = row.find('div', class_='score__blob')
            if score_blob:
                stroller_data['Overall Score'] = score_blob.get_text().strip()
            
            # Get price
            price_label = row.find('label', attrs={'data-price': True})
            if price_label:
                stroller_data['Price'] = price_label.get_text().strip()
            
            # Get ratings
            ratings = row.find_all('div', class_='cell__rating')
            for rating in ratings:
                rating_label = rating.get('aria-label', '')
                if rating_label:
                    score = rating.find('label', attrs={'data-score': True})
                    if score:
                        stroller_data[rating_label.split()[0]] = score.get_text().strip()
            
            # Get attributes
            attributes = row.find_all('div', class_='cell__attribute')
            for attr in attributes:
                attr_label = attr.get('aria-label', '')
                if attr_label:
                    label = attr.find('label')
                    if label:
                        # Extract the attribute name from the aria-label
                        attr_name = attr_label.split(' ', 1)[0]
                        stroller_data[attr_name] = label.get_text().strip()
            
            if stroller_data:
                strollers.append(stroller_data)
        
        return strollers

    def close(self):
        self.driver.quit()

def main():
    url = "https://www.consumerreports.org/babies-kids/strollers/traditional-stroller/c28734"
    scraper = StrollerTableScraper()
    strollers = scraper.scrape_table(url)
    scraper.close()
    if not strollers:
        print("No stroller data found. The page structure might have changed or requires login.")
        return
    with open('strollers_data.json', 'w') as f:
        json.dump(strollers, f, indent=2)
    print(f"\nScraped {len(strollers)} strollers successfully!")
    print("Data saved to strollers_data.json")

if __name__ == "__main__":
    main()
