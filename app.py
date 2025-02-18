from flask import Flask, request, jsonify, render_template
import pandas as pd
import requests
import os

app = Flask(__name__)

# Function to check token status
def check_token_status(token):
    try:
        # Replace with a real token validation URL or logic
        url = "https://api.example.com/validate"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        return response.status_code == 200  # 200 means valid token
    except Exception as e:
        print(f"Error: {e}")
        return False

# API endpoint for file upload and token validation
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    try:
        # Assuming the file is a CSV with a 'token' column
        df = pd.read_csv(file)
        if 'token' not in df.columns:
            return jsonify({'error': 'File must contain a "token" column'}), 400
        
        # Check tokens
        df['status'] = df['token'].apply(check_token_status)
        live_tokens = df[df['status'] == True]
        dead_tokens = df[df['status'] == False]

        # Save results
        live_tokens.to_csv('live_tokens.csv', index=False)
        dead_tokens.to_csv('dead_tokens.csv', index=False)
        
        return jsonify({'message': 'Tokens processed', 
                        'live_count': len(live_tokens), 
                        'dead_count': len(dead_tokens)}), 200

    except Exception as e:
        return jsonify({'error': f'Error processing file: {e}'}), 500

# Serve the index page with the upload form
@app.route('/')
def index():
    return render_template('index.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)

