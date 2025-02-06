import requests

url = "https://open-ai251.p.rapidapi.com/ask"

payload = { "query": "what my name" }
headers = {
	"x-rapidapi-key": "c2fbf89f7fmshdbb0fc4609d3d0dp176c13jsn5cfacb2cead9",
	"x-rapidapi-host": "open-ai251.p.rapidapi.com",
	"Content-Type": "application/json",
	"X-RapidAPI-Key": "4fb84e5862msh93493191641aa67p1730ebjsn9a38755eabe6",
	"X-RapidAPI-Host": "open-ai25.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())


