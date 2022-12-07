"""
Test special day detection
"""

from src.special_days import SpecialDayDetector
from datetime import datetime

detector = SpecialDayDetector()

print("=" * 80)
print("SPECIAL DAY DETECTION TEST")
print("=" * 80)
print(f"\nToday: {detector.today.strftime('%A, %B %d, %Y')}")
print(f"Time: {detector.now.strftime('%I:%M %p')}")

special_day = detector.get_special_day_info()

if special_day:
    print(f"\nSpecial Day Detected: {special_day['name']}")
    print(f"Emoji: {special_day.get('emoji', 'N/A')}")
    print(f"Context: {special_day.get('context', 'N/A')}")
    print(f"Type: {special_day.get('type', 'N/A')}")

    should_add = detector.should_add_special_context()
    print(f"\nShould add to post: {'YES' if should_add else 'NO'}")

    if should_add:
        prompt_enhancement = detector.get_prompt_enhancement()
        post_context = detector.get_post_context()

        if prompt_enhancement:
            print("\n" + "=" * 80)
            print("PROMPT ENHANCEMENT (sent to AI):")
            print("=" * 80)
            print(prompt_enhancement)

        if post_context:
            print("\n" + "=" * 80)
            print("POST CONTEXT (appended to post):")
            print("=" * 80)
            print(post_context)
else:
    print("\nNo special day detected - regular posting day")

print("\n" + "=" * 80)
