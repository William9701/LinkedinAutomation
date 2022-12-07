"""
LinkedIn OAuth 2.0 Token Generator
This script helps you get an access token for LinkedIn API
"""

import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json

# Your LinkedIn App credentials
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8888/callback"

# Required scopes
SCOPES = ["openid", "profile", "email", "w_member_social"]

# Global variable to store the authorization code
auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback"""

    def do_GET(self):
        global auth_code

        # Parse the authorization code from the callback URL
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if 'code' in params:
            auth_code = params['code'][0]

            # Send success response to browser
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body style="font-family: Arial; padding: 50px; text-align: center;">
                    <h1 style="color: green;">Success!</h1>
                    <p>Authorization code received. You can close this window.</p>
                    <p>Check your terminal for the access token.</p>
                </body>
                </html>
            """)
        else:
            # Error handling
            error = params.get('error', ['Unknown error'])[0]
            error_description = params.get('error_description', [''])[0]

            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body style="font-family: Arial; padding: 50px; text-align: center;">
                    <h1 style="color: red;">Error!</h1>
                    <p>Error: {error}</p>
                    <p>{error_description}</p>
                </body>
                </html>
            """.encode())

    def log_message(self, format, *args):
        # Suppress server logs
        pass


def get_access_token():
    """Complete OAuth flow to get access token"""

    print("=" * 80)
    print("LinkedIn OAuth 2.0 Token Generator")
    print("=" * 80)

    # Step 1: Generate authorization URL
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }

    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(auth_params)}"

    print("\nStep 1: Opening LinkedIn authorization page in your browser...")
    print(f"If browser doesn't open, visit this URL manually:")
    print(f"\n{auth_url}\n")

    # Open browser for authorization
    webbrowser.open(auth_url)

    # Step 2: Start local server to receive callback
    print("Step 2: Waiting for authorization callback...")
    print("(A local server is running on http://localhost:8888)")

    server = HTTPServer(('localhost', 8888), CallbackHandler)

    # Wait for one request (the callback)
    server.handle_request()
    server.server_close()

    if not auth_code:
        print("\nError: No authorization code received!")
        return None

    print(f"\nStep 3: Authorization code received!")

    # Step 3: Exchange authorization code for access token
    print("Step 4: Exchanging code for access token...")

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    try:
        response = requests.post(token_url, data=token_data)

        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            expires_in = token_info.get('expires_in')

            print("\n" + "=" * 80)
            print("SUCCESS! Your LinkedIn Access Token:")
            print("=" * 80)
            print(f"\nAccess Token: {access_token}")
            print(f"\nExpires in: {expires_in} seconds ({expires_in // 86400} days)")
            print("\n" + "=" * 80)

            # Save to .env file
            print("\nSaving to .env file...")

            try:
                # Read existing .env or create new
                try:
                    with open('.env', 'r') as f:
                        env_content = f.read()
                except FileNotFoundError:
                    env_content = ""

                # Update or add LinkedIn credentials
                env_lines = env_content.split('\n')
                updated = False

                for i, line in enumerate(env_lines):
                    if line.startswith('LINKEDIN_ACCESS_TOKEN='):
                        env_lines[i] = f'LINKEDIN_ACCESS_TOKEN={access_token}'
                        updated = True
                        break

                if not updated:
                    env_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}')

                # Also add client ID and secret if not present
                has_client_id = any(line.startswith('LINKEDIN_CLIENT_ID=') for line in env_lines)
                has_client_secret = any(line.startswith('LINKEDIN_CLIENT_SECRET=') for line in env_lines)

                if not has_client_id:
                    env_lines.append(f'LINKEDIN_CLIENT_ID={CLIENT_ID}')
                if not has_client_secret:
                    env_lines.append(f'LINKEDIN_CLIENT_SECRET={CLIENT_SECRET}')

                # Write back
                with open('.env', 'w') as f:
                    f.write('\n'.join(env_lines))

                print("Saved to .env file!")

            except Exception as e:
                print(f"Warning: Could not save to .env file: {e}")
                print("Please manually add this to your .env file:")
                print(f"LINKEDIN_ACCESS_TOKEN={access_token}")

            print("\n" + "=" * 80)
            print("Next steps:")
            print("1. Your access token is now saved in .env")
            print("2. Run: python main.py test")
            print("3. This will create a test post on LinkedIn!")
            print("=" * 80)

            return access_token

        else:
            print(f"\nError getting access token:")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"\nError: {str(e)}")
        return None


if __name__ == "__main__":
    print("\nIMPORTANT SETUP REQUIRED:")
    print("=" * 80)
    print("Before running this script, you need to add the redirect URI to your")
    print("LinkedIn app settings:")
    print()
    print("1. Go to: https://www.linkedin.com/developers/apps")
    print(f"2. Select your app (Client ID: {CLIENT_ID})")
    print("3. Go to 'Auth' tab")
    print("4. Under 'OAuth 2.0 settings' -> 'Redirect URLs'")
    print(f"5. Add this URL: {REDIRECT_URI}")
    print("6. Click 'Update'")
    print()
    print("Also verify these products are added to your app:")
    print("  - Sign In with LinkedIn using OpenID Connect")
    print("  - Share on LinkedIn")
    print("=" * 80)

    input("\nPress ENTER when you've completed the setup above...")

    get_access_token()
