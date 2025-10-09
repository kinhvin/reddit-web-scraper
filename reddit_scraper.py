import time
import httpx
import pandas as pd

base_url = "https://www.reddit.com"
endpoint = "/r/10xPennyStocks"
category = "/hot"

url = base_url + endpoint + category + ".json"
after_post_id = None

dataset = []

for _ in range(5):
    params = {
        "limit": 25,
        "t": "week", # time unit (hour, day, week, month, year, all)
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
    df.to_csv("reddit_data.csv", index=False)