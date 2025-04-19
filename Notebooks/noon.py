import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd

def fetch_page_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    try:
        response = session.get(url, headers=headers, timeout=30)  # Increase timeout to 30 seconds
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def fetch_page_content_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(r"D:\projects\noon_amazon\New folder\chromedriver-win64\chromedriver.exe")  # Replace with the path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        return driver.page_source
    finally:
        driver.quit()

def parse_content(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    except Exception as e:
        print(f"Error parsing the content: {e}")
        return None

def main():
    # Fetch the main page content
    url = "https://www.noon.com/egypt-en/electronics/"  # Replace with the main page URL
    html_content = fetch_page_content_with_selenium(url)
    if html_content:
        soup = parse_content(html_content)
        if soup:
            # Find all category containers
            categories_container = soup.find_all('div', class_='BannerModuleStrip_bannerContainer__vm3DD')
            for container in categories_container:
                # Extract link
                link_tag = container.find('a')
                link = link_tag['href'] if link_tag else None

                if link:
                    # Construct the full URL for the category
                    base_url = f"https://www.noon.com{link}"

                    # Loop through sub-pages
                    products = []
                    for i in range(1, 20):  # Adjust the range as needed
                        print(f"Scraping page {i} of category: {base_url}")
                        sub_page_url = f"{base_url}?page={i}"  # Append the page number to the URL
                        sub_page_content = fetch_page_content_with_selenium(sub_page_url)
                        if sub_page_content:
                            sub_page_soup = parse_content(sub_page_content)
                            if sub_page_soup:
                                # Find all product containers
                                product_containers = sub_page_soup.find_all('div', class_='ProductBoxVertical_wrapper__xPj_f')
                                for container in product_containers:
                                    # Extract title
                                    title_tag = container.find('h2', class_='ProductDetailsSection_title__JorAV')
                                    title = title_tag.get_text(strip=True) if title_tag else "N/A"

                                    # Extract price
                                    price_tag = container.find('strong', class_='Price_amount__2sXa7')
                                    price = price_tag.get_text(strip=True) if price_tag else "N/A"

                                    # Extract offer
                                    offer_tag = container.find('span', class_='PriceDiscount_discount__1ViHb')
                                    offer = offer_tag.get_text(strip=True) if offer_tag else "N/A"

                                    # Append product info to the list
                                    products.append({
                                        "title": title,
                                        "price": price,
                                        "offer": offer,
                                        "category": link.split('/')[-2],  # Extract category name from the link
                                        "site": "noon"
                                    })

                    # Save all products for this category to a CSV file
                    if products:
                        category_name = link.split('/')[-2]  # Extract category name from the link
                        file_name = f"{category_name}_products.csv"
                        df = pd.DataFrame(products)
                        df.to_csv(file_name, index=False, encoding='utf-8-sig')
                        print(f"Saved products to {file_name}")

if __name__ == "__main__":
    main()