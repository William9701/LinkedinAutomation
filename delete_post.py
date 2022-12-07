"""
Delete a LinkedIn post by URN
"""
import requests
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
post_urn = "urn:li:share:7403314886816075776"

headers = {
    "Authorization": f"Bearer {access_token}",
    "X-Restli-Protocol-Version": "2.0.0"
}

# URL encode the URN
encoded_urn = urllib.parse.quote(post_urn, safe='')

# Delete the post
delete_url = f"https://api.linkedin.com/v2/ugcPosts/{encoded_urn}"
print(f"Deleting: {delete_url}")
response = requests.delete(delete_url, headers=headers)

if response.status_code in [200, 204]:
    print(f"Successfully deleted post: {post_urn}")
else:
    print(f"Failed to delete: {response.status_code}")
    print(response.text)
