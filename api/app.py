import os

import requests
from flask import Flask, jsonify, Response, request, send_from_directory
from flask_cors import CORS
import yaml
from datetime import datetime

app = Flask(__name__)

debug = 'debug.json' in os.listdir()

PORT = 4995

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
CORS(app, origins=[f"http://localhost:{PORT}", "https://chat.openai.com"])

@app.route('/find_tv_show', methods=['GET'])
def get_tv_show():
    query = request.args.get('q')
    print(query)

    limit = request.args.get('limit')

    # need onconnect api
    url = 'http://data.tmsapi.com/v1.1/programs/search'

    api_key = 'haus4e28u73uuy7jdhphvnbe'

    params = {
        'q':query,
        'api_key':api_key,
        'query_fields':'title',
        'subType':'series'
    }

    response = requests.get(url,params=params)

    if response.status_code != 200:
        return jsonify({"error": "Unable to fetch data from the external API."}), 500

    data = response.json()

    if limit and len(data)>limit:
        data = data[:limit]

    output = {
        'source':{'name':'Gracenote Data'},
        'data':data
    }

    return jsonify(output)


@app.route('/find_movies_near_me', methods=['GET'])
def find_movies_near_me():
    now_time = datetime.now()
    datestring = now_time.strftime('%Y-%m-%d')
    zipcode = request.args.get('zip')
    url = 'http://data.tmsapi.com/v1.1/movies/showings'
    api_key = 'haus4e28u73uuy7jdhphvnbe'

    params = {
        'startDate': datestring,
        'zip': zipcode,
        'api_key': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Unable to fetch data from the external API."}), 500

    raw_data = response.json()
    filtered_data = [
        {
            'name': movie['title'],
            'description': movie.get('longDescription', 'Description not available'),
            'genre': movie.get('genres', ['Unknown']),
            'topCast': movie.get('topCast', ['Unknown']),
            'preferredImageURI': movie.get('preferredImage', {}).get('uri', 'Image not available')
        } 
        for movie in raw_data
    ]

    output = {
        'source': {'name': 'Gracenote Data'},
        'data': filtered_data
    }

    return jsonify(output)



@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    plugin_filename = 'ai-plugin-debug.json' if debug else 'ai-plugin.json'
    return send_from_directory(os.path.dirname(__file__), plugin_filename)


@app.route('/logo.png')
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), 'logo.png')


@app.route('/openai.yaml')
def serve_openapi_yaml():
    with open(os.path.join(os.path.dirname(__file__), 'openai.yaml'), 'r') as f:
        yaml_data = f.read()
    if debug:
        yaml_data = yaml_data.replace('https://chatgpt.deepdigits.pizza',f'http://localhost:{PORT}')
    yaml_data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    return jsonify(yaml_data)


@app.route('/legal')
def legal():
    html = 'data provided by gracenote'
    return html

@app.route('/')
def main():
    html = 'this is the start of a gracenote chatgpt plugin api'
    return html


if __name__ == '__main__':
    app.run(port=PORT,debug=True)
