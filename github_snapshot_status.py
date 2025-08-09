
# import requests

# url = "https://api.brightdata.com/datasets/v3/progress/s_me4qj8kmpzrt1alqq"
# headers = {
# 	"Authorization": "Bearer 9e96796d39db31bfe73251152f7d1851aeb6e90123d2186d9b64faee43137106",
# }

# response = requests.get(url, headers=headers)
# print(response.json())

# Collect by Search URL
import requests

url = "https://api.brightdata.com/datasets/v3/progress/s_me4s3rqm100fw9ebvy"
headers = {
	"Authorization": "Bearer 9e96796d39db31bfe73251152f7d1851aeb6e90123d2186d9b64faee43137106",
}

response = requests.get(url, headers=headers)
print(response.json())