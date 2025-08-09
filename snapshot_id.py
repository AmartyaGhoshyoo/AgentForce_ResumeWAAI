import requests
from dotenv import load_dotenv
import os
load_dotenv()

url = "https://api.brightdata.com/datasets/v3/progress/s_me4t9fvp41b65wkfo"
headers = {
	"Authorization": f"Bearer {os.getenv('Bright')}",
}

response = requests.get(url, headers=headers)
print(response.json())
# import requests

# url = "https://api.brightdata.com/datasets/v3/snapshot/s_me4nit7v2ajvd2tf30"
# headers = {
	# "Authorization": f"Bearer {os.getenv('Bright')}",
# }
# params = {
# 	"format": "json",
# }

# response = requests.get(url, headers=headers, params=params)
# print(response.json())