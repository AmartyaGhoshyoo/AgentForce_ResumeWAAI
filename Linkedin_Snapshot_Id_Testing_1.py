import requests
from dotenv import load_dotenv
import os
load_dotenv()

url = "https://api.brightdata.com/datasets/v3/progress/s_me5qjmg51j9wlm0z9p"
headers = {
	"Authorization": f"Bearer {os.getenv('Bright')}",
 "Content-Type": "application/json",
}

response = requests.get(url, headers=headers)
status_data=response.json()
print(status_data)


# url = "https://api.brightdata.com/datasets/v3/snapshot/s_me4nit7v2ajvd2tf30"
# headers = {
# 	"Authorization": f"Bearer {os.getenv('Bright')}",
# }
# params = {
# 	"format": "json",
# }

# response = requests.get(url, headers=headers, params=params)
# print(response.json())