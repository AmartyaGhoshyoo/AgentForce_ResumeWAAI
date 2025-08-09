import requests

url = "https://api.brightdata.com/datasets/v3/progress/s_me4t9fvp41b65wkfo"
headers = {
	"Authorization": "Bearer 9e96796d39db31bfe73251152f7d1851aeb6e90123d2186d9b64faee43137106",
}

response = requests.get(url, headers=headers)
print(response.json())
# import requests

# url = "https://api.brightdata.com/datasets/v3/snapshot/s_me4nit7v2ajvd2tf30"
# headers = {
# 	"Authorization": "Bearer 9e96796d39db31bfe73251152f7d1851aeb6e90123d2186d9b64faee43137106",
# }
# params = {
# 	"format": "json",
# }

# response = requests.get(url, headers=headers, params=params)
# print(response.json())