# # Discover by Serach URL
# import requests

# url = "https://api.brightdata.com/datasets/v3/trigger"
# headers = {
# 	"Authorization": "Bearer 9e96796d39db31bfe73251152f7d1851aeb6e90123d2186d9b64faee43137106",
# 	"Content-Type": "application/json",
# }
# params = {
# 	"dataset_id": "gd_lyrexgxc24b3d4imjt",
# 	"include_errors": "true",
# 	"type": "discover_new",
# 	"discover_by": "search_url",
# }
# data = [
# 	{"url":"https://github.com/AmartyaGhoshyoo?tab=repositories"},
# ]

# response = requests.post(url, headers=headers, params=params, json=data)
# print(response.json())

# Collect by URL 
import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
	"Authorization": "Bearer 9e96796d39db31bfe73251152f7d1851aeb6e90123d2186d9b64faee43137106",
	"Content-Type": "application/json",
}
params = {
	"dataset_id": "gd_lyrexgxc24b3d4imjt",
	"include_errors": "true",
	"type": "discover_new",
	"discover_by": "url",
}
data = [
	{"repo_url":"https://github.com/AmartyaGhoshyoo/AgentForce_ResumeWAAI"},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())