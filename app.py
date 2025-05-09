from flask import Flask, render_template, request, jsonify
import json
import os
from estimator import estimate_price
from geocoding import geocode_location
from routing import get_route
from search import search_properties

app = Flask(__name__)

# Load properties data
def load_properties():
    with open('static/data/properties.json') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/properties', methods=['GET'])
def get_properties():
    properties = load_properties()
    return jsonify(properties)

@app.route('/api/search', methods=['POST'])
def property_search():
    search_criteria = request.json
    results = search_properties(search_criteria, load_properties())
    return jsonify(results)

@app.route('/api/estimate-price', methods=['POST'])
def price_estimation():
    features = request.json
    price = estimate_price(features)
    return jsonify({'estimated_price': price})

@app.route('/api/geocode', methods=['GET'])
def geocode():
    location = request.args.get('location')
    coordinates = geocode_location(location)
    return jsonify(coordinates)

@app.route('/api/route', methods=['GET'])
def route():
    start_lat = float(request.args.get('start_lat'))
    start_lng = float(request.args.get('start_lng'))
    end_lat = float(request.args.get('end_lat'))
    end_lng = float(request.args.get('end_lng'))
    
    route_data = get_route(start_lat, start_lng, end_lat, end_lng)
    return jsonify(route_data)

if __name__ == '__main__':
    # Ensure the data directory exists
    os.makedirs('static/data', exist_ok=True)
    
    # Create properties.json if it doesn't exist
    if not os.path.exists('static/data/properties.json'):
        with open('static/data/properties.json', 'w') as f:
            json.dump([], f)
    
    app.run(debug=True)