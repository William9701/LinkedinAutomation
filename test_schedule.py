"""
Test the new daily scheduling
"""
from src.scheduler import PostScheduler
from datetime import datetime

scheduler = PostScheduler(timezone="UTC")

def dummy_post():
    print("Post would be created here")

# Schedule the posts
scheduler.schedule_daily_posts(
    post_callback=dummy_post,
    morning_time="09:00",
    evening_time="19:00"
)

# Start the scheduler to get next run times
scheduler.start()

print("=" * 80)
print("LINKEDIN AUTOMATION - DAILY POSTING SCHEDULE")
print("=" * 80)
print("\nCurrent Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))
print("\nScheduled Jobs:")
print("-" * 80)

try:
    for job_info in scheduler.get_next_run_times():
        print(f"\n{job_info['name']}:")
        print(f"  Next Run: {job_info['next_run']}")
except:
    # Fallback if get_next_run_times fails
    for job in scheduler.scheduler.get_jobs():
        print(f"\n{job.name}:")
        print(f"  Trigger: {job.trigger}")

scheduler.stop()

print("\n" + "=" * 80)
print("SCHEDULE DETAILS:")
print("=" * 80)
print("\nFrequency: EVERY DAY (Monday - Sunday)")
print("Morning Post: ~9:00 AM UTC (±30 minutes)")
print("Evening Post: ~7:00 PM UTC (±30 minutes)")
print("\nTotal Posts: 2 per day = 14 per week = ~730 per year")
print("\nDynamic Timing: Each run has random ±30min variance")
print("This makes posts look more natural and organic!")
print("=" * 80)
