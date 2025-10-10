# Reddit Stock Scraper
A simple Python script that scrapes posts from multiple subreddits about penny stocks and uploads them to Google Sheets. Great for tracking trending discussions or doing some light analysis. Right now this is mostly for my own personal usage and experimentation.

## Features
  - Scrapes Reddit posts from multiple subreddits
  - Supports different categories
  - Only pulls relevant and useful data into the dataset
  - Creates a local CSV copy of the dataset
  - Automatically uploads the dataset to the connected Google Sheet

## Project Future
  - I've hardcoded details like the subreddits that are scraped, the amount of posts to get per scrape, and the timeframes of the posts for my own personal usage
    - I was thinking of maybe scaling this into a small web application with a GUI that gives the option to choose these values rather than having them harcoded
  - Would like to integrate AI to analyze the data using a free model from OpenRouter

## Requirements
- Libraries:
  - `httpx`
  - `pandas`
  - `gspread`
  - `oauth2client`
