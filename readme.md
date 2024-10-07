# Instagram Reels Scraper with Selenium and SQLite

## Overview

This project is an automated Instagram Reels scraper built using Python, Selenium, SQLite, and requests. The scraper navigates Instagram profiles to extract Reels, downloads the associated videos, and saves relevant data (reel URLs, date and time, video source URLs, and local file paths) to an SQLite database. It can run in continuous cycles, scraping a configurable number of Reels from multiple profiles defined in a JSON file. The scraper navigates to the Instagram homepage between cycles, staying efficient without closing the browser after every scrape.

## Features

1. **Reel Scraping**: Extracts Instagram Reels URLs, timestamps, and video links from profile pages.
2. **Video Downloading**: Downloads 720p Instagram Reel videos and saves them locally.
3. **SQLite Database**: Saves Reel data (URL, timestamp, video URL, and download path) in an SQLite database.
4. **Cycles & Cooldown**: Runs continuously in cycles with a customizable cooldown period between cycles.
5. **Multiple Profiles**: Scrapes Reels from multiple Instagram profiles, listed in a `users.json` file.
6. **No Browser Restart**: The browser remains open throughout each cycle and navigates to the next page without closing. At the end of each cycle, it navigates back to Instagram's homepage.

## Prerequisites

- **Python 3.x**
- **Google Chrome**
- **ChromeDriver** (automatically managed by `webdriver_manager`)
- **Selenium** (`pip install selenium`)
- **WebDriverManager** (`pip install webdriver-manager`)
- **Requests** (`pip install requests`)

## Project Structure

- **`main.py`**: Main script containing the scraping logic.
- **`users.json`**: A JSON file containing Instagram profile URLs to scrape.
- **`scraped.db`**: SQLite database where the Reel data is stored.
- **`/Page-Content`**: Directory where HTML snapshots of Instagram pages are saved.
- **`/Downloads`**: Directory where the downloaded Instagram videos are stored.

### Example JSON file (`users.json`):
```json
{
    "pages": [
        "https://www.instagram.com/profile1/",
        "https://www.instagram.com/profile2/",
        "https://www.instagram.com/profile3/"
    ]
}


```

### Installation

    Clone the Repository:

```bash

git clone https://github.com/your-repo/IG-Sync-Scraper.git
cd IG-Sync-Scraper


```


Install Dependencies: Install the required Python libraries:

```bash

pip install selenium webdriver-manager requests

```

Configure Chrome User Data: Update the path for user-data-dir in the script with your actual Chrome user data directory:

```python

options.add_argument("user-data-dir=C:/path/to/your/Chrome/User Data")

```

Set up the JSON File: Create a users.json file in the project root directory and add the Instagram profile URLs you want to scrape:

```json

{
    "pages": [
        "https://www.instagram.com/profile1/",
        "https://www.instagram.com/profile2/"
    ]
}


```


Run the Scraper: Execute the main script:

```bash

    python main.py

```

### How It Works

    Initialization: The SQLite database is initialized with a table (reels) if it doesn’t already exist.
    Profile Scraping: The script iterates through the Instagram profiles defined in the users.json file.
    Reel Data Extraction: For each profile, the script scrolls through the page, collects Reels' URLs, and extracts their publication time and video source URL.
    Video Download: The 720p video is downloaded for each Reel, and the local path is saved in the SQLite database.