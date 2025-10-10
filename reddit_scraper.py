import time
import httpx
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Connect to Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# Set up the client
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account_creds.json", scope)
client = gspread.authorize(creds)

# Open the spreadsheet
sheet = client.open("Reddit Scraping").sheet1

# Set up the Reddit API
base_url = "https://www.reddit.com"
subreddits = ["10xPennyStocks", "pennystocks", "Pennystock", "PennyStockProfits", "buzztickr"]
category = input("Enter a valid category (best, hot, new, top, rising): ")
dataset = []

# Scrape posts from each subreddit
for sub in subreddits:
    url = f"{base_url}/r/{sub}/{category}.json"
    after_post_id = None
    print(f"\nScraping r/{sub}...")
    
    # Scrape posts from respective subreddit
    for _ in range(5):
        
        if sub == "buzztickr":
            params = {
                "limit": 1,
                "t": "week", # time unit (hour, day, week, month, year, all)
                "after": after_post_id
            }
        
        else:
            params = {
                "limit": 20,
                "t": "month", # time unit (hour, day, week, month, year, all)
                "after": after_post_id
            }
        
        response = httpx.get(url, params=params)
        print(f"fetching {response.url}...")
        if response.status_code != 200:
            raise Exception("Failed to fetch data")
        
        data = response.json()
        dataset.extend(rec["data"] for rec in data["data"]["children"])
        
        after_post_id = data["data"]["after"]
        
        # Add a delay to avoid 429 errors
        time.sleep(0.5)
    
df = pd.DataFrame(dataset)

# Only include relevant columns in the dataset
df = df[["subreddit", "title", "ups", "downs", "num_comments", "url", "author"]]

# Create a local CSV copy of the dataset
df.to_csv("reddit_data.csv", index=False)

# Clear the current sheet and upload the new data to it
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())
print(f"\nData uploaded to Google Sheets at {sheet.url}")