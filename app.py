from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

# Facebook API Configuration
FB_API_VERSION = "v19.0"
FB_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"

def get_profile_info(access_token):
    """Fetch profile information from Facebook Graph API"""
    try:
        # Get basic profile info
        profile_response = requests.get(
            f"{FB_API_BASE}/me",
            params={
                'fields': 'id,name,email,birthday,link',
                'access_token': access_token
            },
            timeout=10
        )
        profile_response.raise_for_status()
        profile_data = profile_response.json()

        # Get profile picture
        picture_response = requests.get(
            f"{FB_API_BASE}/me/picture",
            params={
                'redirect': 'false',
                'type': 'large',
                'access_token': access_token
            },
            timeout=10
        )
        picture_response.raise_for_status()
        picture_data = picture_response.json()

        # Get posts count
        posts_response = requests.get(
            f"{FB_API_BASE}/me/feed",
            params={
                'limit': 0,
                'summary': 'true',
                'access_token': access_token
            },
            timeout=10
        )
        posts_response.raise_for_status()
        posts_data = posts_response.json()

        return {
            'id': profile_data.get('id'),
            'name': profile_data.get('name'),
            'email': profile_data.get('email'),
            'birthday': profile_data.get('birthday'),
            'profile_link': profile_data.get('link'),
            'picture': picture_data['data']['url'],
            'posts_count': posts_data.get('summary', {}).get('total_count', 0)
        }

    except requests.exceptions.HTTPError as e:
        error = e.response.json().get('error', {})
        return {'error': error.get('message', 'Unknown error')}
    except Exception as e:
        return {'error': str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    profile_info = None
    error = None
    
    if request.method == 'POST':
        access_token = request.form.get('access_token', '').strip()
        if access_token:
            profile_info = get_profile_info(access_token)
            if 'error' in profile_info:
                error = profile_info['error']
                profile_info = None

    return render_template('index.html', profile=profile_info, error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
