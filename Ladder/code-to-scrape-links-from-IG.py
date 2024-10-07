import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to scroll and load more posts
def scroll_down(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust the sleep time based on your network speed
        logging.info("Scrolled down to load more posts.")
    except Exception as e:
        logging.error(f"Error during scrolling: {e}")

# Initialize WebDriver with user profile (make sure Chrome is closed when running this)
options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")  # Disable browser notifications
options.add_argument("user-data-dir=C:/Users/Ymir/AppData/Local/Google/Chrome/User Data")  # Path to your Chrome user data
options.add_argument("profile-directory=Profile 5")  # Your profile directory (could be "Profile 1", "Default", etc.)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the Instagram profile page
url = "https://www.instagram.com/libyan4insta/"  # Replace with the actual Instagram profile URL
logging.info(f"Opening Instagram profile page: {url}")
driver.get(url)

# Scroll down to load posts
for _ in range(2):  # Initial scroll down to ensure some posts are loaded
    scroll_down(driver)

# Wait for the posts to appear
try:
    post_selector = "a[href*='/reel/']"  # CSS selector for post links
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, post_selector)))
    logging.info("Posts loaded successfully.")
except Exception as e:
    logging.error(f"Error loading posts: {e}")
    driver.quit()
    exit()

# Initialize variables for collecting post URLs
post_urls = []
max_posts = 20  # Limit to 20 URLs

# Scroll, extract post URLs, and repeat until we have 20 post URLs
while len(post_urls) < max_posts:
    logging.info("Extracting post URLs.")

    try:
        # Locate all post links using the CSS selector
        posts = driver.find_elements(By.CSS_SELECTOR, post_selector)
        
        # Loop through posts and collect URLs
        for post in posts:
            post_url = post.get_attribute('href')

            if post_url not in post_urls:  # Avoid duplicates
                post_urls.append(post_url)
                logging.info(f"Post found: {post_url}")
                print(f"Post URL: {post_url}")

            # Break if we have collected enough post URLs
            if len(post_urls) >= max_posts:
                break

        # Scroll down to load more posts if we haven't reached 20 posts yet
        if len(post_urls) < max_posts:
            logging.info(f"Collected {len(post_urls)} posts. Scrolling for more.")
            scroll_down(driver)

    except Exception as e:
        logging.error(f"Error extracting posts: {e}")
        driver.quit()
        exit()

# Print the total number of post URLs collected
logging.info(f"Collected {len(post_urls)} post URLs.")
print(f"Collected {len(post_urls)} post URLs.")

# Close the browser
driver.quit()
logging.info("Browser closed.")
