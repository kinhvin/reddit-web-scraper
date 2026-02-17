import time
import httpx
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

""" CONSTANTS """
BASE_URL = "https://www.reddit.com"
SUBREDDITS = ["10xPennyStocks", "pennystocks", "Pennystock", "PennyStockProfits", "buzztickr"]
VALID_CATEGORIES = ["best", "hot", "new", "top", "rising"]
SPREADSHEET_NAME = "Reddit Scraping"
CSV_OUTPUT_FILE = "reddit_data.csv"
COLUMNS_TO_KEEP = ["subreddit", "title", "ups", "downs", "num_comments", "url", "author"]
RATE_LIMIT_DELAY = 0.5 # delay in seconds to avoid hitting Reddit's rate limits
RATE_LIMIT_RETRY_DELAY = 10
REQUEST_LIMIT = 100 # max number of posts to request (Reddit's hard limit)
MAX_POSTS = 499

""" STATUS CODES """
RESPONSE_OK = 200
TOO_MANY_REQUESTS = 429

""" Connect to Google Sheets API using gspread and google-auth """
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets", 
    "https://www.googleapis.com/auth/drive"
]

# Set up the credentials object
CREDENTIALS_PATH = "credentials/service_account_creds.json"
creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=GOOGLE_SCOPES)

# Authorize with the credentials object
client = gspread.authorize(creds)

# Open the spreadsheet
sheet = client.open(SPREADSHEET_NAME).sheet1

# Get the category from the user
while True:
    category = input("Enter a valid category (best, hot, new, top, rising): ")
    if category in VALID_CATEGORIES:
        break
    print("Invalid category. Please try again.")

dataset = []

# Scrape posts from each subreddit
for sub in SUBREDDITS:
    posts_fetched = 0
    after_post_id = None
    url = f"{BASE_URL}/r/{sub}/{category}.json"
    print(f"\nScraping r/{sub}...")

    while posts_fetched < MAX_POSTS:
        posts_remaining = MAX_POSTS - posts_fetched
        req_limit = min(posts_remaining, REQUEST_LIMIT)
    
        params = {
            "limit": req_limit,
            "after": after_post_id
        }

        # Fetch posts from the subreddit using the specified category and pagination
        response = httpx.get(url, params=params)
        print(f"fetching {response.url}...")
        if response.status_code == TOO_MANY_REQUESTS:
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(RATE_LIMIT_RETRY_DELAY) # Wait before retrying
            continue
        elif response.status_code != RESPONSE_OK:
            print(f"Error {response.status_code} while fetching data from r/{sub}, skipping to next page")
            continue

        data = response.json()

        new_posts = [child["data"] for child in data["data"]["children"]]
        dataset.extend(new_posts)
        posts_fetched += len(new_posts)

        after_post_id = data["data"]["after"]

        # Stop if there are no more posts to fetch
        if not after_post_id or len(new_posts) == 0:
            break
        
        time.sleep(RATE_LIMIT_DELAY)
    
df = pd.DataFrame(dataset)

# Only include relevant columns in the dataset
df = df[COLUMNS_TO_KEEP]

# Create a local CSV copy of the dataset
df.to_csv(CSV_OUTPUT_FILE, index=False)

# Clear the current sheet and upload the new data to it
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())
print(f"\nData uploaded to Google Sheets at {sheet.url}")