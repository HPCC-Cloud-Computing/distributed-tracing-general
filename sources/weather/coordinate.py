import json
import requests

def getCoordinate(address):
    address = address.strip()
    print address
    baseUrl = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key='
    MAP_APIKEY = 'AIzaSyCR5tsp-oDawrBfogR6olArOLrqUSMduK4'

    response = requests.get(baseUrl + MAP_APIKEY)

    #coordinate =  response.text.results[0].geometry.location
    data = json.loads(response.text)
    coordinate = data['results'][0]['geometry']['location']
    return coordinate
