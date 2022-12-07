"""
Simple LinkedIn OAuth - Run this and follow the steps
"""

import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = ["openid", "profile", "email", "w_member_social"]

auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1 style="color: green;">Success!</h1>
                <p>You can close this window and check your terminal.</p>
                </body></html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error = params.get('error', ['Unknown'])[0]
            self.wfile.write(f"<html><body><h1>Error: {error}</h1></body></html>".encode())

    def log_message(self, format, *args):
        pass

# Step 1: Build auth URL
auth_params = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': ' '.join(SCOPES)
}
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(auth_params)}"

print("=" * 80)
print("LinkedIn OAuth - Getting Access Token")
print("=" * 80)
print("\nStep 1: Opening browser for LinkedIn login...")
print(f"URL: {auth_url}\n")

webbrowser.open(auth_url)

print("Step 2: Waiting for callback on http://localhost:8888 ...")
print("(Authorize the app in your browser)")

server = HTTPServer(('localhost', 8888), CallbackHandler)
server.handle_request()
server.server_close()

if not auth_code:
    print("\nERROR: No authorization code received!")
    exit(1)

print(f"\nStep 3: Got authorization code!")
print("Step 4: Exchanging for access token...")

token_url = "https://www.linkedin.com/oauth/v2/accessToken"
token_data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': REDIRECT_URI
}

response = requests.post(token_url, data=token_data)

if response.status_code == 200:
    token_info = response.json()
    access_token = token_info['access_token']
    expires_in = token_info['expires_in']

    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    print(f"\nAccess Token:\n{access_token}")
    print(f"\nExpires in: {expires_in} seconds ({expires_in // 86400} days)")

    # Save to .env
    try:
        with open('.env', 'a') as f:
            f.write(f"\nLINKEDIN_ACCESS_TOKEN={access_token}\n")
        print("\nSaved to .env file!")
    except:
        print("\nCouldn't save to .env - add manually:")
        print(f"LINKEDIN_ACCESS_TOKEN={access_token}")

    print("\n" + "=" * 80)
    print("Next: Run 'python main.py test' to post to LinkedIn!")
    print("=" * 80)
else:
    print(f"\nERROR: {response.status_code}")
    print(response.text)
