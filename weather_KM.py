import datetime as dt
import json

import requests
from flask import Flask, jsonify, request


API_TOKEN = ""

API_KEY = ""  #https://www.visualcrossing.com/account - to get your key

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

def generate_weather(location: str, date: str):
    url_base = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    UnitGroup='uk'

    url = f"{url_base}/{location}/{date}?&unitGroup={UnitGroup}&key={API_KEY}"
    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        weather_data = json.loads(response.text)

        weather_data = {
            "temp_c": weather_data.get("days")[0].get("temp"),
            "description": weather_data.get("days")[0].get("description"),
            "pressure_mb": weather_data.get("days")[0].get("pressure"),
            "humidity": weather_data.get("days")[0].get("humidity"),
            "wind_kph": weather_data.get("days")[0].get("windspeed")       
        }
        
        return weather_data
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)
        

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA weather MK Saas.</h2></p>"

@app.route("/content/api/weather/integration/generate", methods=["POST"])
def weather_endpoint():
    
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)
    if json_data.get("requester_name") is None:
        raise InvalidUsage("requester_name is required", status_code=400)
    if json_data.get("location") is None:
        raise InvalidUsage("location is required", status_code=400)
    if json_data.get("date") is None:
        raise InvalidUsage("date is required", status_code=400)
    

    token = json_data.get("token")
    requester_name = json_data.get("requester_name")
    location = json_data.get("location")
    date = json_data.get("date")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    weather = generate_weather(location, date)

    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    result = {
  
        "timestamp": timestamp,
        "requester_name": requester_name,
        "location": location,
        "date": date,
        "weather": weather,
    }

    return result