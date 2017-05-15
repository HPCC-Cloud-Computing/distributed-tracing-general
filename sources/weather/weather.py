import requests
import json

def getWeather(lat, lng):
    #sample api key for get weather
    APIKEY = '0d6592b48108138b9dbf80c55676b0de'
    #https://api.forecast.io/forecast/APIKEY/LATITUDE,LONGITUDE
    baseUrl = 'https://api.forecast.io/forecast/'

    url = baseUrl + APIKEY + '/' + str(lat) + ','+ str(lng)
    #print url
    response = requests.get(url) 

    if (response.status_code == 200):
        weatherInfor = json.loads(response.text)
        #print weatherInfor['currently']
        currentWeatherInfor = weatherInfor['currently']
        return currentWeatherInfor

        
    

        