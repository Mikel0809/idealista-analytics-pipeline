import requests

url = "https://idealista7.p.rapidapi.com/listbuildings"

querystring = {
	"order":"relevance",
	"operation":"sale",
	"locationId":"0-EU-ES-28",
	"locationName":"Madrid",
	"numPage":"1",
	"maxItems":"40",
	"location":"es",
	"locale":"es"}

headers = {
	"x-rapidapi-key": "c6c0c2ce9dmsh09426791611cbf9p140451jsn73d5830bb4bb",
	"x-rapidapi-host": "idealista7.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())