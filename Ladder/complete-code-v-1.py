import time
import logging
import re
import os
import json
import csv
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
        time_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a/span/time[@datetime]'))
        )
        date_time = time_element.get_attribute('datetime')
        logging.info(f"Date and time found: {date_time}")
        return date_time
    except Exception as e:
        logging.error(f"Could not extract date/time: {e}")
        return None

# Function to extract the 720p video URL based on the shortcode
def extract_720p_video_url(file_path, shortcode):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        shortcode_pattern = re.compile(r'{"items":\[{"code":"' + re.escape(shortcode) + r'".*?"video_versions":(\[.*?\])')
        shortcode_match = shortcode_pattern.search(html_content)

        if shortcode_match:
            video_versions_json = shortcode_match.group(1)
            video_versions = json.loads(video_versions_json)

            for video in video_versions:
                if video.get("width") == 720:
                    video_url = video.get("url").replace("\\u0026", "&")
                    logging.info(f"720p Video URL found: {video_url}")
                    return video_url

            logging.info("No 720p video URL found.")
        else:
            logging.info(f"No video versions found for shortcode: {shortcode}")
    except Exception as e:
        logging.error(f"Error extracting video URL: {e}")
    return None

# Function to scroll and load more posts
def scroll_down(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        logging.info("Scrolled down to load more posts.")
    except Exception as e:
        logging.error(f"Error during scrolling: {e}")

# Main function to scrape reels, extract details, and save to CSV
def scrape_reels_to_csv(profile_url, num_reels, save_dir, csv_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("user-data-dir=C:/Users/Ymir/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Profile 5")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the Instagram profile page
        logging.info(f"Opening Instagram profile page: {profile_url}")
        driver.get(profile_url)

        # Scroll down to load posts
        for _ in range(2):
            scroll_down(driver)

        # Wait for posts to appear
        post_selector = "a[href*='/reel/']"
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, post_selector)))
        
        post_urls = []
        max_posts = num_reels

        # Scroll and collect reel URLs
        while len(post_urls) < max_posts:
            logging.info("Extracting post URLs.")
            posts = driver.find_elements(By.CSS_SELECTOR, post_selector)
            for post in posts:
                post_url = post.get_attribute('href')
                if post_url not in post_urls:
                    post_urls.append(post_url)
                    logging.info(f"Post found: {post_url}")
                if len(post_urls) >= max_posts:
                    break
            if len(post_urls) < max_posts:
                scroll_down(driver)

        # Prepare CSV file
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Reel Link', 'Date Time', 'Video URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Process each reel URL
            for reel_url in post_urls:
                driver.get(reel_url)
                time.sleep(5)

                # Extract the shortcode and save HTML
                shortcode = reel_url.split('/')[-2]
                html_save_path = os.path.join(save_dir, f"{shortcode}.html")
                save_complete_html(driver, html_save_path)

                # Extract the date and time
                date_time = extract_date_time(driver)

                # Extract the video URL
                video_url = extract_720p_video_url(html_save_path, shortcode)

                # Write to CSV
                writer.writerow({
                    'Reel Link': reel_url,
                    'Date Time': date_time,
                    'Video URL': video_url
                })
                logging.info(f"Reel processed: {reel_url}")

        logging.info(f"All reels processed. Data saved to {csv_path}.")

    except Exception as e:
        logging.error(f"Error processing Instagram profile: {e}")
    finally:
        driver.quit()
        logging.info("Browser closed.")

# Example usage
profile_url = "https://www.instagram.com/libyan4insta/"  # Replace with the actual profile URL
num_reels = 20  # Number of reels to scrape
save_dir = "C:/Users/Ymir/Desktop/Git Adventure/War Room/Page-Content"  # Directory to save the HTML
csv_path = "C:/Users/Ymir/Desktop/Git Adventure/War Room/scraped.csv"  # Path to save the CSV

scrape_reels_to_csv(profile_url, num_reels, save_dir, csv_path)
