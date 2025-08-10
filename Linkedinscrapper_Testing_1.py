import requests
from dotenv import load_dotenv
import os
load_dotenv()

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
	"Authorization": f"Bearer {os.getenv('Bright')}",
	"Content-Type": "application/json",
}
params = {
	"dataset_id": "gd_l1viktl72bvl7bjuj0",
	"include_errors": "true",
}
data = [
	{"url":"https://www.linkedin.com/in/amartya-ghosh-2b9b7b22b/"},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())