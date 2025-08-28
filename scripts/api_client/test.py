import requests

url = "https://idealista7.p.rapidapi.com/propertydetails"

querystring = {"propertyId":"101535118","location":"es","language":"en"}

headers = {
	"x-rapidapi-key": "c6c0c2ce9dmsh09426791611cbf9p140451jsn73d5830bb4bb",
	"x-rapidapi-host": "idealista7.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())