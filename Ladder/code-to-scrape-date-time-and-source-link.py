import time
import logging
import re
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to save the complete HTML content of the page
def save_complete_html(driver, save_path):
    try:
        html_source = driver.page_source
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_source)
        logging.info(f"Complete HTML saved at {save_path}")
    except Exception as e:
        logging.error(f"Error saving HTML: {e}")

# Function to extract the date and time of the post
def extract_date_time(driver):
    try:
        # Use the relative XPath to find the time element
        time_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a/span/time[@datetime]'))
        )
        date_time = time_element.get_attribute('datetime')
        logging.info(f"Date and time found: {date_time}")
        print(f"Date and time: {date_time}")
    except Exception as e:
        logging.error(f"Could not extract date/time: {e}")
        print(f"Error extracting date/time: {e}")

# Function to extract the 720p video URL based on the shortcode
def extract_720p_video_url(file_path, shortcode):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Look for the JSON-like structure that contains the shortcode
        shortcode_pattern = re.compile(r'{"items":\[{"code":"' + re.escape(shortcode) + r'".*?"video_versions":(\[.*?\])')
        shortcode_match = shortcode_pattern.search(html_content)

        if shortcode_match:
            video_versions_json = shortcode_match.group(1)
            video_versions = json.loads(video_versions_json)

            # Loop through video versions to find the 720p version
            for video in video_versions:
                if video.get("width") == 720:
                    video_url = video.get("url").replace("\\u0026", "&")  # Replace the escaped characters
                    logging.info(f"720p Video URL found: {video_url}")
                    print(f"720p Video URL: {video_url}")
                    return video_url

            logging.info("No 720p video URL found.")
            print("No 720p video URL found.")
        else:
            logging.info(f"No video versions found for shortcode: {shortcode}")
            print(f"No video versions found for shortcode: {shortcode}")

    except Exception as e:
        logging.error(f"Error extracting video URL: {e}")
        print(f"Error extracting video URL: {e}")

# Main function to load Instagram post, save HTML, and extract details
def test_post_extraction(post_url, save_dir):
    # Initialize WebDriver with Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("user-data-dir=C:/Users/Ymir/AppData/Local/Google/Chrome/User Data")  
    options.add_argument("profile-directory=Profile 5")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
    options.add_argument("--log-level=1")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        logging.info(f"Opening post URL: {post_url}")
        driver.get(post_url)
        
        # Wait for the page to load
        time.sleep(5)

        # Save the complete HTML of the page
        shortcode = post_url.split('/')[-2]  # Extract the shortcode from the URL
        html_save_path = os.path.join(save_dir, f"{shortcode}.html")
        save_complete_html(driver, html_save_path)

        # Extract the date and time of the post
        extract_date_time(driver)

        # Extract the video URL by parsing the saved HTML
        extract_720p_video_url(html_save_path, shortcode)

    except Exception as e:
        logging.error(f"Error processing Instagram post: {e}")
    finally:
        driver.quit()
        logging.info("Browser closed.")

# Example usage
post_url = "https://www.instagram.com/p/DAwmqvDqY6z/"  # Replace with the actual post URL
save_dir = "C:/Users/Ymir/Desktop/Git Adventure/War Room"  # Directory to save the HTML
test_post_extraction(post_url, save_dir)
