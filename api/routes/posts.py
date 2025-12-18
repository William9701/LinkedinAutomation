from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import logging
from pathlib import Path
import shutil
import time

from config import settings
from src.topic_manager import TopicManager
from src.content_generator import ContentGenerator
from src.image_generator import ImageGenerator
from src.linkedin_poster import LinkedInPoster
from api.models import (
    CustomPostRequest, 
    PostResponse, 
    GeneratePreviewRequest, 
    PreviewResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize components
topic_manager = TopicManager()
content_generator = ContentGenerator(settings.gemini_api_key)
image_generator = ImageGenerator(
    openai_api_key=settings.openai_api_key,
    replicate_token=settings.replicate_api_token
)
linkedin_poster = LinkedInPoster(settings.linkedin_access_token)


@router.post("/post/random", response_model=PostResponse)
async def create_random_post():
    """
    Create and post a random LinkedIn post using an unused topic
    """
    try:
        logger.info("Creating random post...")
        
        # Get unused topic
        topic = topic_manager.get_unused_topic()
        if not topic:
            raise HTTPException(status_code=404, detail="No topics available")
        
        logger.info(f"Selected topic: {topic['title']}")
        
        # Generate content
        post_content = content_generator.generate_post_content(topic)
        if not post_content:
            raise HTTPException(status_code=500, detail="Failed to generate content")
        
        # Generate hashtags
        hashtags = content_generator.optimize_hashtags(topic, post_content)
        
        # Generate image (optional)
        image_path = None
        image_prompt = content_generator.generate_image_prompt(topic, post_content)
        if image_prompt:
            image_path = image_generator.generate_image(
                image_prompt,
                filename=f"topic_{topic['id']}"
            )
        
        # Post to LinkedIn
        if image_path and Path(image_path).exists():
            post_urn = linkedin_poster.create_image_post(
                content=post_content,
                image_path=image_path,
                hashtags=hashtags
            )
        else:
            post_urn = linkedin_poster.create_text_post(
                content=post_content,
                hashtags=hashtags
            )
        
        if post_urn:
            topic_manager.mark_topic_used(topic['id'])
            return PostResponse(
                success=True,
                message="Post created successfully",
                post_urn=post_urn,
                content=post_content,
                hashtags=hashtags
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to post to LinkedIn")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating random post: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/custom", response_model=PostResponse)
async def create_custom_post(
    topic: str = Form(...),
    prompt: Optional[str] = Form(None),
    category: str = Form("General"),
    image: Optional[UploadFile] = File(None)
):
    """
    Create a custom LinkedIn post with user-provided topic, prompt, and optional image
    """
    try:
        logger.info(f"Creating custom post with topic: {topic}")
        
        # Create custom topic dict
        custom_topic = {
            "id": 0,
            "category": category,
            "title": topic,
            "prompt": prompt or f"Write a LinkedIn post about: {topic}"
        }
        
        # Generate content
        post_content = content_generator.generate_post_content(custom_topic)
        if not post_content:
            raise HTTPException(status_code=500, detail="Failed to generate content")
        
        # Generate hashtags
        hashtags = content_generator.optimize_hashtags(custom_topic, post_content)
        
        # Handle uploaded image
        image_path = None
        if image:
            # Save uploaded image
            upload_dir = Path("generated_images")
            upload_dir.mkdir(exist_ok=True)
            image_path = upload_dir / f"custom_{int(time.time())}_{image.filename}"
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            logger.info(f"Uploaded image saved: {image_path}")
        
        # Post to LinkedIn
        if image_path and Path(image_path).exists():
            post_urn = linkedin_poster.create_image_post(
                content=post_content,
                image_path=str(image_path),
                hashtags=hashtags
            )
        else:
            post_urn = linkedin_poster.create_text_post(
                content=post_content,
                hashtags=hashtags
            )
        
        if post_urn:
            return PostResponse(
                success=True,
                message="Custom post created successfully",
                post_urn=post_urn,
                content=post_content,
                hashtags=hashtags
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to post to LinkedIn")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating custom post: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-preview", response_model=PreviewResponse)
async def generate_preview(request: GeneratePreviewRequest):
    """
    Generate a preview of content without posting to LinkedIn
    """
    try:
        logger.info(f"Generating preview for topic: {request.topic}")
        
        # Create topic dict
        topic_dict = {
            "id": 0,
            "category": request.category,
            "title": request.topic,
            "prompt": request.prompt or f"Write a LinkedIn post about: {request.topic}"
        }
        
        # Generate content
        post_content = content_generator.generate_post_content(topic_dict)
        if not post_content:
            raise HTTPException(status_code=500, detail="Failed to generate content")
        
        # Generate hashtags
        hashtags = content_generator.optimize_hashtags(topic_dict, post_content)
        
        # Generate image prompt
        image_prompt = content_generator.generate_image_prompt(topic_dict, post_content)
        
        return PreviewResponse(
            content=post_content,
            hashtags=hashtags,
            image_prompt=image_prompt
        )
        
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
