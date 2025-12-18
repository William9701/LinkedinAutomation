from fastapi import APIRouter, HTTPException
from typing import List
import logging

from src.topic_manager import TopicManager
from api.models import StatusResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize topic manager
topic_manager = TopicManager()


@router.get("/topics")
async def get_all_topics():
    """
    Get all available topics
    """
    try:
        topics = topic_manager.get_all_topics()
        return {
            "total": len(topics),
            "topics": topics
        }
        
    except Exception as e:
        logger.error(f"Error loading topics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics/unused")
async def get_unused_topics():
    """
    Get all unused topics
    """
    try:
        all_topics = topic_manager.get_all_topics()
        unused = [t for t in all_topics if not t.get("used", False)]
        
        return {
            "total": len(unused),
            "topics": unused
        }
        
    except Exception as e:
        logger.error(f"Error loading unused topics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics/categories")
async def get_categories():
    """
    Get all unique topic categories
    """
    try:
        all_topics = topic_manager.get_all_topics()
        categories = list(set(t.get("category", "General") for t in all_topics))
        categories.sort()
        
        return {
            "total": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error loading categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topics/reset")
async def reset_topics():
    """
    Reset all topics to unused state
    """
    try:
        topic_manager.reset_all_topics()
        
        return {
            "success": True,
            "message": "All topics reset to unused"
        }
        
    except Exception as e:
        logger.error(f"Error resetting topics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get API status and statistics
    """
    try:
        all_topics = topic_manager.get_all_topics()
        unused_topics = [t for t in all_topics if not t.get("used", False)]
        
        # Get next scheduled post from schedule
        from .schedule import get_next_post
        next_post_data = await get_next_post()
        next_scheduled = None
        if next_post_data.get("next_post"):
            next_post = next_post_data["next_post"]
            next_scheduled = f"{next_post.date} {next_post.time}"
        
        return StatusResponse(
            status="healthy",
            total_topics=len(all_topics),
            unused_topics=len(unused_topics),
            next_scheduled_post=next_scheduled
        )
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
