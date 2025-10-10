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
endpoint = "/r/10xPennyStocks"
category = "/best"
url = base_url + endpoint + category + ".json"
after_post_id = None
dataset = []

# Scrape 500 posts from within the last month
for _ in range(5):
    params = {
        "limit": 100,
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
    time.sleep(0.5)
    
df = pd.DataFrame(dataset)

# Sanitize the data of instances of list and dict
for col in df.columns:
    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)

# Sanitize the data of any inf or -inf
df = df.replace([float('inf'), float('-inf')], None).fillna("")
df.to_csv("reddit_data.csv", index=False)

# Clear the current sheet and upload the new CSV data to it
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())
print(f"Data uploaded to Google Sheets at {sheet.url}")