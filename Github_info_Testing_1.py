import requests

url = "https://api.brightdata.com/datasets/v3/snapshot/s_me4qj8kmpzrt1alqq"
headers = {
	"Authorization": f"Bearer {os.getenv('Bright')}",
}
params = {
	"format": "json",
}

response = requests.get(url, headers=headers, params=params)
print(response.json())