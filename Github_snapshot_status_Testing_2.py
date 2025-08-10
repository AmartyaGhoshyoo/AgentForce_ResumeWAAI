
# import requests

# url = "https://api.brightdata.com/datasets/v3/progress/s_me4qj8kmpzrt1alqq"
# headers = {
	"Authorization": f"Bearer {os.getenv('Bright')}",
# }

# response = requests.get(url, headers=headers)
# print(response.json())

# Collect by Search URL
import requests

url = "https://api.brightdata.com/datasets/v3/progress/s_me4s3rqm100fw9ebvy"
headers = {
	"Authorization": f"Bearer {os.getenv('Bright')}",
}

response = requests.get(url, headers=headers)
print(response.json())