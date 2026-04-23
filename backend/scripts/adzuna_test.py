import requests

import os
from dotenv import load_dotenv

# Tell Python to find and load your specific file
# If the file is in the same folder as this script:
load_dotenv("keys.env") 

# Now pull the values into your script
APP_ID = os.getenv("API_ID")
APP_KEY = os.getenv("APP_KEY")

url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": 5,
    "what": "data analyst",
    "where": "india"
}

response = requests.get(url, params=params)
data = response.json()



for job in data["results"]:
    print("TITLE:", job["title"])
    print("COMPANY:", job["company"]["display_name"])
    print("DESCRIPTION:", job["description"][:200])  # first 200 chars
    print("-" * 50)