import requests

APP_ID = "f9e7aa2a"
APP_KEY = "b950747941f707dd9027083b425d8e79"

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