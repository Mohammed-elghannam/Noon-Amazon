import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re

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

def extract_see_all_results_link(container):
    # Find the "See all results" link
    see_all_link_tag = container.find('a', id='apb-desktop-browse-search-see-all')
    see_all_link = see_all_link_tag['href'] if see_all_link_tag else None
    return see_all_link

def extract_pagination_links(soup):
    """Extract all pagination links from the 'See all results' page."""
    pagination_container = soup.find('div', class_='s-pagination-container')
    if not pagination_container:
        return []

    # Find all pagination links
    pagination_links = pagination_container.find_all('a', class_='s-pagination-item')
    return [f"https://www.amazon.eg{link['href']}" for link in pagination_links if link.get('href')]


def scrape_category_products(category_name, see_all_link):
    """Scrape all products from the 'See all results' pages."""
    products = []
    current_page_url = see_all_link


    while current_page_url:
        print(f"Scraping page: {current_page_url}")
        page_content = fetch_page_content_with_selenium(current_page_url)
        if not page_content:
            break

        soup = parse_content(page_content)
        if not soup:
            break

        # Extract product details
        product_containers = soup.find_all('div', class_='sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20')
        for container in product_containers:
            # Extract product name
            name_tag = container.find('h2', class_='a-size-base-plus a-spacing-none a-color-base a-text-normal')
            name = name_tag.get_text(strip=True) if name_tag else "N/A"
            # Extract price
            price_tag = container.find('span', class_='a-price-whole')
            price = price_tag.get_text(strip=True) if price_tag else "N/A"

            # Extract rating
            rating_tag = container.find('span', class_='a-icon-alt')
            rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

            # Extract number of reviews
            reviews_tag = container.find('span', class_='a-size-base')
            reviews = reviews_tag.get_text(strip=True) if reviews_tag else "N/A"

            # Extract offer
            #offer_tag = container.find('span', class_='a-offscreen')
            #offer = offer_tag.get_text(strip=True) if offer_tag else "N/A"

            # استخراج السعر
            price_whole_tag = container.find('span', class_='a-price-whole')
            price_fraction_tag = container.find('span', class_='a-price-fraction')
            
            if price_whole_tag:
                price_text = price_whole_tag.get_text(strip=True)
                if price_fraction_tag:
                    price_text += '.' + price_fraction_tag.get_text(strip=True)
                price = price_text
            else:
                price = "N/A"

            # استخراج السعر الأصلي قبل الخصم
            original_price_tag = container.find('span', class_='a-price a-text-price')
            original_price_span = original_price_tag.find('span', class_='a-offscreen') if original_price_tag else None
            original_price = original_price_span.get_text(strip=True) if original_price_span else "N/A"

            # Append product info to the list
            products.append({
                "name": name,
                "price": price,
                "Original Price": original_price,
                "category": category_name,
                "site": "amazon"
            })

        # Find the next page link
        next_page_tag = soup.find('a', class_='s-pagination-next')
        if next_page_tag and 'href' in next_page_tag.attrs:
            current_page_url = f"https://www.amazon.eg{next_page_tag['href']}"
        else:
            current_page_url = None  # No more pages

    return products

def main():
    # Fetch the main page content
    url = "https://www.amazon.eg/-/en/%D8%A5%D9%84%D9%83%D8%AA%D8%B1%D9%88%D9%86%D9%8A%D8%A7%D8%AA/b/?ie=UTF8&node=18018102031&ref_=nav_cs_electronics"  # Replace with the main page URL
    html_content = fetch_page_content_with_selenium(url)
    if html_content:
        soup = parse_content(html_content)
        if soup:
            # Find all category containers
            categories_container = soup.find('div', class_='sl-sobe-carousel-viewport-row')
            category_links = categories_container.find_all('a', class_='sl-sobe-carousel-sub-card-link')
            
            for category_link in category_links:
                # Extract category name and link
                category_name = category_link['aria-label']
                category_url = f"https://www.amazon.eg{category_link['href']}"
                print(f"Scraping category: {category_name} - {category_url}")
                
                # Fetch the category page to find the "See all results" link
                category_page_content = fetch_page_content_with_selenium(category_url)
                if category_page_content:
                    category_soup = parse_content(category_page_content)
                    if category_soup:
                        # Extract the "See all results" link
                        see_all_link = extract_see_all_results_link(category_soup)
                        if see_all_link:
                            full_see_all_link = f"https://www.amazon.eg{see_all_link}"
                            print(f"See all results link for {category_name}: {full_see_all_link}")
                            
                            # Scrape all products from the "See all results" pages
                            products = scrape_category_products(category_name, full_see_all_link)
                            
                            # Save products to a CSV file
                            if products:
                                file_name = f"{category_name}_products.csv"
                                df = pd.DataFrame(products)
                                df.to_csv(file_name, index=False, encoding='utf-8-sig')
                                print(f"Saved products to {file_name}")

if __name__ == "__main__":
    main()