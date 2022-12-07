import requests
import logging
from typing import Optional, Dict
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class LinkedInPoster:
    """Posts content to LinkedIn using the LinkedIn API"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202501"
        }
        self._user_id = None

    def get_user_info(self) -> Optional[Dict]:
        """Get the authenticated user's profile information using userinfo endpoint"""
        try:
            # Use OpenID Connect userinfo endpoint
            url = "https://api.linkedin.com/v2/userinfo"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                # Store the sub (subject) which is the user ID
                self._user_id = user_data.get('sub')
                return user_data
            else:
                logger.error(f"Failed to get user info: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return None

    def create_text_post(self, content: str, hashtags: list = None) -> Optional[str]:
        """
        Create a text-only post on LinkedIn

        Args:
            content: Post content
            hashtags: List of hashtags (without #)

        Returns:
            Post URN if successful, None otherwise
        """
        try:
            # Get user ID
            user_info = self.get_user_info()
            if not user_info:
                logger.error("Could not retrieve user info")
                return None

            user_id = self._user_id or user_info.get("sub")
            if not user_id:
                logger.error("User ID not found in response")
                return None

            # Format hashtags
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                full_content = f"{content}\n\n{hashtag_text}"
            else:
                full_content = content

            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": full_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # Post to LinkedIn
            url = f"{self.base_url}/ugcPosts"
            response = requests.post(url, headers=self.headers, json=post_data, timeout=30)

            if response.status_code == 201:
                post_urn = response.headers.get("x-restli-id")
                logger.info(f"Post created successfully: {post_urn}")
                return post_urn
            else:
                logger.error(f"Failed to create post: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating text post: {str(e)}")
            return None

    def upload_image(self, image_path: str, user_id: str) -> Optional[str]:
        """
        Upload an image to LinkedIn

        Args:
            image_path: Path to image file
            user_id: LinkedIn user ID

        Returns:
            Image asset URN if successful
        """
        try:
            # Step 1: Register upload
            register_url = f"{self.base_url}/assets?action=registerUpload"
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{user_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            response = requests.post(
                register_url,
                headers=self.headers,
                json=register_data,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Failed to register upload: {response.status_code} - {response.text}")
                return None

            upload_data = response.json()
            asset = upload_data["value"]["asset"]
            upload_url = upload_data["value"]["uploadMechanism"][
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
            ]["uploadUrl"]

            # Step 2: Upload the image
            with open(image_path, "rb") as f:
                image_data = f.read()

            upload_headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            upload_response = requests.put(
                upload_url,
                headers=upload_headers,
                data=image_data,
                timeout=60
            )

            if upload_response.status_code in [200, 201]:
                logger.info(f"Image uploaded successfully: {asset}")
                return asset
            else:
                logger.error(f"Failed to upload image: {upload_response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return None

    def create_image_post(
        self,
        content: str,
        image_path: str,
        hashtags: list = None
    ) -> Optional[str]:
        """
        Create a post with an image on LinkedIn

        Args:
            content: Post content
            image_path: Path to image file
            hashtags: List of hashtags (without #)

        Returns:
            Post URN if successful
        """
        try:
            # Get user ID
            user_info = self.get_user_info()
            if not user_info:
                logger.error("Could not retrieve user info")
                return None

            user_id = user_info.get("id")
            if not user_id:
                logger.error("User ID not found")
                return None

            # Upload image
            image_asset = self.upload_image(image_path, user_id)
            if not image_asset:
                logger.error("Failed to upload image, posting text only")
                return self.create_text_post(content, hashtags)

            # Format hashtags
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                full_content = f"{content}\n\n{hashtag_text}"
            else:
                full_content = content

            # Prepare post data with image
            post_data = {
                "author": f"urn:li:person:{user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": full_content
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": "Post image"
                                },
                                "media": image_asset,
                                "title": {
                                    "text": "Post"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # Post to LinkedIn
            url = f"{self.base_url}/ugcPosts"
            response = requests.post(url, headers=self.headers, json=post_data, timeout=30)

            if response.status_code == 201:
                post_urn = response.headers.get("x-restli-id")
                logger.info(f"Post with image created successfully: {post_urn}")
                return post_urn
            else:
                logger.error(f"Failed to create post with image: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating image post: {str(e)}")
            return None
