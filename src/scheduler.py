from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
import pytz
import logging

logger = logging.getLogger(__name__)


class PostScheduler:
    """Schedules LinkedIn posts at optimal times"""

    # Optimal posting times based on research for maximum engagement
    # These are generally when professionals are most active on LinkedIn
    OPTIMAL_TIMES = {
        "morning": "09:00",      # Tuesday-Thursday 9 AM (people checking LinkedIn at work start)
        "evening": "18:00",      # Tuesday-Thursday 6 PM (after work, high engagement)
        "midday": "12:00",       # Wednesday 12 PM (lunch break)
    }

    # Best days for LinkedIn engagement (weekdays, especially Tue-Thu)
    OPTIMAL_DAYS = {
        "morning": "tue-thu",    # Tuesday to Thursday
        "evening": "tue-thu",    # Tuesday to Thursday
    }

    def __init__(self, timezone: str = "UTC"):
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone(timezone))
        self.timezone = timezone
        self.jobs = []

    def schedule_daily_posts(
        self,
        post_callback,
        morning_time: str = None,
        evening_time: str = None
    ):
        """
        Schedule two daily posts EVERY DAY with dynamic timing

        Args:
            post_callback: Function to call when it's time to post
            morning_time: Base time for morning post (HH:MM format), defaults to 09:00
            evening_time: Base time for evening post (HH:MM format), defaults to 19:00
        """
        import random

        morning_time = morning_time or "09:00"
        evening_time = evening_time or "19:00"

        # Parse base times
        morning_hour, morning_minute = map(int, morning_time.split(':'))
        evening_hour, evening_minute = map(int, evening_time.split(':'))

        # Add random variance to make timing dynamic (±30 minutes)
        morning_variance = random.randint(-30, 30)
        evening_variance = random.randint(-30, 30)

        # Calculate actual times
        actual_morning_minute = (morning_minute + morning_variance) % 60
        morning_hour_adjustment = (morning_minute + morning_variance) // 60
        actual_morning_hour = (morning_hour + morning_hour_adjustment) % 24

        actual_evening_minute = (evening_minute + evening_variance) % 60
        evening_hour_adjustment = (evening_minute + evening_variance) // 60
        actual_evening_hour = (evening_hour + evening_hour_adjustment) % 24

        # Schedule morning post EVERY DAY
        morning_job = self.scheduler.add_job(
            post_callback,
            CronTrigger(
                day_of_week='mon-sun',  # Every day!
                hour=actual_morning_hour,
                minute=actual_morning_minute,
                timezone=self.timezone
            ),
            id='morning_post',
            name='Morning LinkedIn Post',
            replace_existing=True
        )
        self.jobs.append(morning_job)
        logger.info(f"Scheduled DAILY morning posts around {morning_time} (±30min variance)")

        # Schedule evening post EVERY DAY
        evening_job = self.scheduler.add_job(
            post_callback,
            CronTrigger(
                day_of_week='mon-sun',  # Every day!
                hour=actual_evening_hour,
                minute=actual_evening_minute,
                timezone=self.timezone
            ),
            id='evening_post',
            name='Evening LinkedIn Post',
            replace_existing=True
        )
        self.jobs.append(evening_job)
        logger.info(f"Scheduled DAILY evening posts around {evening_time} (±30min variance)")

    def schedule_custom_post(
        self,
        post_callback,
        hour: int,
        minute: int,
        day_of_week: str = 'mon-fri',
        job_id: str = None
    ):
        """
        Schedule a custom post time

        Args:
            post_callback: Function to call when it's time to post
            hour: Hour (0-23)
            minute: Minute (0-59)
            day_of_week: Days to post (e.g., 'mon-fri', 'tue-thu', 'mon,wed,fri')
            job_id: Optional job ID
        """
        job = self.scheduler.add_job(
            post_callback,
            CronTrigger(
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
                timezone=self.timezone
            ),
            id=job_id,
            replace_existing=True
        )
        self.jobs.append(job)
        logger.info(f"Scheduled custom post for {day_of_week} at {hour:02d}:{minute:02d}")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def get_next_run_times(self):
        """Get next scheduled run times for all jobs"""
        next_runs = []
        for job in self.scheduler.get_jobs():
            next_runs.append({
                "job_id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S %Z") if job.next_run_time else "Not scheduled"
            })
        return next_runs

    def is_optimal_time(self, dt: datetime = None) -> bool:
        """
        Check if given time is an optimal posting time

        Args:
            dt: Datetime to check (defaults to now)

        Returns:
            True if it's an optimal time to post
        """
        if dt is None:
            dt = datetime.now(pytz.timezone(self.timezone))

        # Check if it's a weekday (Monday = 0, Sunday = 6)
        if dt.weekday() >= 5:  # Saturday or Sunday
            return False

        # Check if it's during optimal hours
        hour = dt.hour
        # Best times: 7-10 AM, 12-2 PM, 5-8 PM
        optimal_hours = (
            (7 <= hour <= 10) or
            (12 <= hour <= 14) or
            (17 <= hour <= 20)
        )

        return optimal_hours
