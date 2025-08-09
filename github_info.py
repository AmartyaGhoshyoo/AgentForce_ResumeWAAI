import requests

url = "https://api.brightdata.com/datasets/v3/snapshot/s_me4qj8kmpzrt1alqq"
headers = {
	"Authorization": "Bearer 9e96796d39db31bfe73251152f7d1851aeb6e90123d2186d9b64faee43137106",
}
params = {
	"format": "json",
}

response = requests.get(url, headers=headers, params=params)
print(response.json())