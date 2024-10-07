import time
import logging
import re
import os
import json
import sqlite3
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize SQLite Database
def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reels
                 (reel_url TEXT PRIMARY KEY, date_time TEXT, video_url TEXT, video_path TEXT)''')
    conn.commit()
    conn.close()

# Check if the reel already exists in the database
def reel_exists_in_db(db_path, reel_url):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT 1 FROM reels WHERE reel_url = ?", (reel_url,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Save reel data to the SQLite database
def save_reel_to_db(db_path, reel_url, date_time, video_url, video_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO reels (reel_url, date_time, video_url, video_path) VALUES (?, ?, ?, ?)", 
              (reel_url, date_time, video_url, video_path))
    conn.commit()
    conn.close()

# Function to download the video
def download_video(video_url, save_dir):
    video_name = video_url.split('/')[-1].split('?')[0]  # Get video name from URL
    video_path = os.path.join(save_dir, video_name)

    response = requests.get(video_url, stream=True)
    with open(video_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    logging.info(f"Video downloaded successfully as {video_path}")
    return video_path

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
        time.sleep(1)  # Reduce sleep time to improve speed
        logging.info("Scrolled down to load more posts.")
    except Exception as e:
        logging.error(f"Error during scrolling: {e}")

# Main function to scrape reels, extract details, and save to SQLite
def scrape_reels(profile_url, num_reels, save_dir, db_path, download_dir):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("user-data-dir=C:/Users/Ymir/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Profile 5")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
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

        # Process each reel URL
        for reel_url in post_urls:
            if reel_exists_in_db(db_path, reel_url):
                logging.info(f"Reel already exists in DB: {reel_url}")
                continue  # Skip if reel already exists

            driver.get(reel_url)
            time.sleep(1)  # Reduced wait time to improve speed

            # Extract the shortcode and save HTML
            shortcode = reel_url.split('/')[-2]
            html_save_path = os.path.join(save_dir, f"{shortcode}.html")
            save_complete_html(driver, html_save_path)

            # Extract the date and time
            date_time = extract_date_time(driver)

            # Extract the video URL
            video_url = extract_720p_video_url(html_save_path, shortcode)

            if video_url:
                # Download the video
                video_path = download_video(video_url, download_dir)

                # Save the reel data to the SQLite DB
                save_reel_to_db(db_path, reel_url, date_time, video_url, video_path)
                logging.info(f"Reel processed and saved: {reel_url}")

    except Exception as e:
        logging.error(f"Error processing Instagram profile: {e}")
    finally:
        driver.quit()
        logging.info("Browser closed.")

# Function to read page URLs from users.json
def read_pages_from_json(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['pages']

# Function to run the scraper in cycles
def run_in_cycles(json_path, num_reels, save_dir, db_path, download_dir, cooldown_minutes):
    while True:
        cycle_start_time = datetime.now()
        logging.info(f"Cycle started at: {cycle_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        pages = read_pages_from_json(json_path)
        for page in pages:
            logging.info(f"Going to page: {page}")
            scrape_reels(page, num_reels, save_dir, db_path, download_dir)

        logging.info(f"Cycle finished. Cooling down for {cooldown_minutes} minutes.")
        time.sleep(cooldown_minutes * 60)  # Cool down before the next cycle

# Example usage
json_path = "C:/Users/Ymir/Desktop/Git Adventure/War Room/users.json"  # Path to users.json file
num_reels = 5  # Number of reels to scrape per page
save_dir = "C:/Users/Ymir/Desktop/Git Adventure/War Room/Page-Content"  # Directory to save the HTML
download_dir = "C:/Users/Ymir/Desktop/Git Adventure/War Room/Downloads"  # Directory to save downloaded videos
db_path = "C:/Users/Ymir/Desktop/Git Adventure/War Room/scraped.db"  # Path to the SQLite database
cooldown_minutes = 3  # Cooldown time between cycles (in minutes)

# Initialize the database
init_db(db_path)

# Run the scraper in cycles
run_in_cycles(json_path, num_reels, save_dir, db_path, download_dir, cooldown_minutes)
