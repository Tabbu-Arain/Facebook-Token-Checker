from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
FACEBOOK_API_VERSION = os.getenv('FACEBOOK_API_VERSION', 'v19.0')

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def verify_token():
    data = request.get_json()
    access_token = data.get('access_token')
    
    if not access_token:
        return jsonify({'error': 'No token provided'}), 400
    
    try:
        # Verify token with Facebook
        fb_url = f'https://graph.facebook.com/{FACEBOOK_API_VERSION}/me'
        params = {
            'fields': 'id,name,email,birthday,picture.width(300)',
            'access_token': access_token
        }
        
        response = requests.get(fb_url, params=params, timeout=10)
        response.raise_for_status()
        user_data = response.json()
        
        return jsonify(user_data)
    
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': 'Invalid token or API error'}), 401
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Connection error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', False))
