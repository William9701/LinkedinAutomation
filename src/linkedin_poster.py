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
                logger.info(f"Retrieved user info - sub: {self._user_id}")
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

            user_id = self._user_id or user_info.get("sub")
            if not user_id:
                logger.error(f"User ID not found. user_info: {user_info}, _user_id: {self._user_id}")
                return None

            logger.info(f"Using user_id: {user_id}")

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

    def add_comment_to_post(self, post_urn: str, comment_text: str) -> bool:
        """
        Add a comment to a LinkedIn post

        Args:
            post_urn: URN of the post to comment on
            comment_text: Comment content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user ID
            if not self._user_id:
                user_info = self.get_user_info()
                if not user_info:
                    logger.error("Could not retrieve user info for comment")
                    return False

            user_id = self._user_id
            if not user_id:
                logger.error("User ID not available")
                return False

            # Prepare comment data
            comment_data = {
                "actor": f"urn:li:person:{user_id}",
                "object": post_urn,
                "message": {
                    "text": comment_text
                }
            }

            # Post comment
            url = f"{self.base_url}/socialActions/{post_urn}/comments"
            response = requests.post(url, headers=self.headers, json=comment_data, timeout=30)

            if response.status_code == 201:
                logger.info(f"Comment added successfully to post: {post_urn}")
                return True
            else:
                logger.error(f"Failed to add comment: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            return False

    def create_image_post_with_comment(
        self,
        main_content: str,
        comment_content: str,
        image_path: str,
        hashtags: list = None
    ) -> Optional[str]:
        """
        Create a post with an image and add a comment with the solution

        Args:
            main_content: Main post content (the question/hook)
            comment_content: Comment content (the solution/answer)
            image_path: Path to image file
            hashtags: List of hashtags (without #)

        Returns:
            Post URN if successful
        """
        try:
            # First, create the post with image
            post_urn = self.create_image_post(main_content, image_path, hashtags)

            if not post_urn:
                logger.error("Failed to create main post")
                return None

            # Wait a moment for the post to be fully created
            import time
            time.sleep(2)

            # Add the solution as a comment
            comment_success = self.add_comment_to_post(post_urn, comment_content)

            if comment_success:
                logger.info(f"Post with comment created successfully: {post_urn}")
            else:
                logger.warning(f"Post created but comment failed: {post_urn}")

            return post_urn

        except Exception as e:
            logger.error(f"Error creating post with comment: {str(e)}")
            return None

    def create_multi_image_post(
        self,
        content: str,
        image_paths: list,
        hashtags: list = None
    ) -> Optional[str]:
        """
        Create a post with multiple images on LinkedIn

        Args:
            content: Post content
            image_paths: List of paths to image files
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

            user_id = self._user_id or user_info.get("sub")
            if not user_id:
                logger.error(f"User ID not found. user_info: {user_info}, _user_id: {self._user_id}")
                return None

            logger.info(f"Using user_id: {user_id}")

            # Upload all images
            image_assets = []
            for i, image_path in enumerate(image_paths):
                logger.info(f"Uploading image {i+1}/{len(image_paths)}: {image_path}")
                image_asset = self.upload_image(image_path, user_id)
                if not image_asset:
                    logger.error(f"Failed to upload image {i+1}")
                    continue
                image_assets.append(image_asset)

            if not image_assets:
                logger.error("Failed to upload any images, posting text only")
                return self.create_text_post(content, hashtags)

            # Format hashtags
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                full_content = f"{content}\n\n{hashtag_text}"
            else:
                full_content = content

            # Prepare media array with all images
            media_array = []
            for i, asset in enumerate(image_assets):
                media_array.append({
                    "status": "READY",
                    "description": {
                        "text": f"Image {i+1}"
                    },
                    "media": asset,
                    "title": {
                        "text": f"Image {i+1}"
                    }
                })

            # Prepare post data with multiple images
            post_data = {
                "author": f"urn:li:person:{user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": full_content
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": media_array
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
                logger.info(f"Post with {len(image_assets)} images created successfully: {post_urn}")
                return post_urn
            else:
                logger.error(f"Failed to create post with images: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating multi-image post: {str(e)}")
            return None
