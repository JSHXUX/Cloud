from flask import Flask, request, jsonify
import requests
import config
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


BAKUGAN_API_URL = "http://localhost:8000"
@app.route('/bakugan/', methods=['GET', 'POST'])
@app.route('/bakugan/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(subpath=""):
    url = f"{BAKUGAN_API_URL}/bakugan"
    if subpath:
        url += f"/{subpath}"
    data = request.get_json() if request.data else None
    
    try:
        response = requests.request(request.method, url, json=data)
        return (response.content, response.status_code, response.headers.items())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Internal server error"}), 500
    

WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
@app.route('/weather/', methods=['GET'])
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Bad request. Bad content"}), 400
    params = {
        "q": city,
        "appid": config.WEATHER_API_KEY,
        "units": "metric",
        "lang": "ro"
    }
    try:
        response = requests.request(request.method, WEATHER_API_URL, params=params)
        return (response.content, response.status_code, response.headers.items())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Internal server error"}), 500
    

USELESS_API_URL = "https://uselessfacts.jsph.pl/api/v2/facts/random"
@app.route('/useless/', methods=['GET'])
def get_useless_fact():
    try:
        response = requests.request(request.method, USELESS_API_URL)
        print(response)
        return (response.content, response.status_code, response.headers.items())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Internal server error"}), 500
    

if __name__ == '__main__':
    app.run(port=8080, debug=True)