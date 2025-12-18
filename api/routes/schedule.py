from fastapi import APIRouter, HTTPException
from typing import List
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path

from api.models import ScheduleItem

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory schedule storage (can be replaced with database later)
SCHEDULE_FILE = Path("schedule_data.json")


def load_schedule() -> List[dict]:
    """Load schedule from file"""
    if SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    return []


def save_schedule(schedule: List[dict]):
    """Save schedule to file"""
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f, indent=2)


def initialize_default_schedule():
    """Initialize default schedule for the next 7 days"""
    schedule = []
    today = datetime.now()
    
    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Morning post
        schedule.append({
            "date": date_str,
            "time": "09:00",
            "type": "morning",
            "status": "scheduled"
        })
        
        # Evening post
        schedule.append({
            "date": date_str,
            "time": "19:00",
            "type": "evening",
            "status": "scheduled"
        })
    
    save_schedule(schedule)
    return schedule


@router.get("/schedule", response_model=List[ScheduleItem])
async def get_schedule():
    """
    Get the current posting schedule
    """
    try:
        schedule = load_schedule()
        if not schedule:
            schedule = initialize_default_schedule()
        
        # Convert to ScheduleItem models
        return [ScheduleItem(**item) for item in schedule]
        
    except Exception as e:
        logger.error(f"Error loading schedule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedule/{date}")
async def cancel_schedule(date: str, post_type: str = "all"):
    """
    Cancel scheduled posts for a specific date
    
    Args:
        date: Date in YYYY-MM-DD format
        post_type: "morning", "evening", or "all" (default)
    """
    try:
        schedule = load_schedule()
        
        updated_count = 0
        for item in schedule:
            if item["date"] == date:
                if post_type == "all" or item["type"] == post_type:
                    item["status"] = "cancelled"
                    updated_count += 1
        
        if updated_count == 0:
            raise HTTPException(status_code=404, detail=f"No scheduled posts found for {date}")
        
        save_schedule(schedule)
        
        return {
            "success": True,
            "message": f"Cancelled {updated_count} post(s) for {date}",
            "cancelled_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling schedule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/reset")
async def reset_schedule():
    """
    Reset the schedule to default (next 7 days)
    """
    try:
        schedule = initialize_default_schedule()
        return {
            "success": True,
            "message": "Schedule reset to default",
            "schedule": [ScheduleItem(**item) for item in schedule]
        }
        
    except Exception as e:
        logger.error(f"Error resetting schedule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule/next")
async def get_next_post():
    """
    Get the next scheduled post
    """
    try:
        schedule = load_schedule()
        now = datetime.now()
        
        # Find next scheduled (not cancelled) post
        for item in sorted(schedule, key=lambda x: f"{x['date']} {x['time']}"):
            post_datetime = datetime.strptime(f"{item['date']} {item['time']}", "%Y-%m-%d %H:%M")
            if post_datetime > now and item['status'] == 'scheduled':
                return {
                    "next_post": ScheduleItem(**item),
                    "time_until": str(post_datetime - now)
                }
        
        return {
            "next_post": None,
            "message": "No upcoming scheduled posts"
        }
        
    except Exception as e:
        logger.error(f"Error getting next post: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
