from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from urllib.parse import urljoin
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import comparison_bp

# Create Blueprint
scrape_bp = Blueprint("comparison", __name__)
CORS(scrape_bp)  # Enable CORS on blueprint

# Router to detect requests
# TODO: UPDATE ROUTE 
@comparison_bp.route("/api/scrape", methods=["POST"])
def scrape_from_tags():
    try:
        data = request.get_json()
        tags = data.get("tags", [])
        img_urls = scrape_images(tags)
        return jsonify(img_urls), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint for the other function
@comparison_bp.route("/api/compare", methods=["POST"])
def compare_from_scrape():
    try:
        data = request.get_json()
        img_paths = data.get("URLS", [])
        print("IMG_PATHS ARE --> " + str(img_paths))
        # Call the comparison function --> should return a list of URLs and their percent match
        url_and_percent = comparison.calculate_similarity(img_paths)
        print("URL AND PERCENT ARE --> " + str(url_and_percent))
        return jsonify(url_and_percent), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def scrape_images(tags):
    # TODO: remove debugging comments, clean up
    # Configure Selenium to use Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Start the browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    img_urls = []
    for tag in tags: 
        # print("TAG IS --> " + tag)
        # Open Shein search page
        BASE_URL = 'https://dummy-site-1.vercel.app/?search='+tag
        # print("BASE_URL IS --> " + BASE_URL)
        driver.get(BASE_URL)

        # Wait for JavaScript to load
        time.sleep(5)

        # Get page source after JavaScript loads
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # print(soup.prettify())  # Print the parsed HTML for debugging

        # Find images
        images = soup.find_all('img')

        # Append image URLs to a list
        for img in images:
            img_url = img.get('src')
            # print("IMG IS" + img_url)
            if img_url:
                # Convert to absolute URL if it's relative
                full_img_url = urljoin(BASE_URL, img_url)
                # print(full_img_url)
                try:
                    img_urls.append(full_img_url)
                except Exception as e:
                    # print("Error occurred:", e)
                    return jsonify({'error': str(e)}), 500
            # Return the list of image URLs
            # print(img_urls)
        # Close browser
    driver.quit()
    
    return img_urls

if __name__ == "__main__":
    app.run()