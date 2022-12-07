"""
Special day detection and contextual messaging for LinkedIn posts
Adds professional, relevant context for holidays, milestones, and special occasions
"""

from datetime import datetime, date
from typing import Optional, Dict
import calendar


class SpecialDayDetector:
    """Detects special days and provides professional contextual messages"""

    # Tech industry holidays and observances
    TECH_HOLIDAYS = {
        (1, 1): {"name": "New Year's Day", "emoji": "🎊", "context": "new beginnings", "type": "major"},
        (2, 14): {"name": "Valentine's Day", "emoji": "❤️", "context": "appreciation", "type": "minor"},
        (3, 8): {"name": "International Women's Day", "emoji": "👩‍💻", "context": "women in tech", "type": "major"},
        (3, 14): {"name": "Pi Day", "emoji": "🥧", "context": "mathematics and engineering", "type": "tech"},
        (5, 4): {"name": "Star Wars Day", "emoji": "⭐", "context": "May the 4th", "type": "fun"},
        (7, 4): {"name": "Independence Day (US)", "emoji": "🎆", "context": "independence", "type": "major"},
        (9, 12): {"name": "Programmers' Day", "emoji": "👨‍💻", "context": "celebrating developers", "type": "tech"},
        (10, 24): {"name": "World Development Information Day", "emoji": "🌍", "context": "global development", "type": "tech"},
        (10, 31): {"name": "Halloween", "emoji": "🎃", "context": "debugging nightmares", "type": "fun"},
        (11, 1): {"name": "World Hello Day", "emoji": "👋", "context": "connection", "type": "minor"},
        (12, 24): {"name": "Christmas Eve", "emoji": "🎄", "context": "holiday season", "type": "major"},
        (12, 25): {"name": "Christmas Day", "emoji": "🎄", "context": "holiday season", "type": "major"},
        (12, 31): {"name": "New Year's Eve", "emoji": "🎉", "context": "year reflection", "type": "major"},
    }

    # Moveable holidays (approximate dates)
    MOVEABLE_HOLIDAYS = [
        "Thanksgiving",
        "Black Friday",
        "Cyber Monday",
    ]

    def __init__(self):
        self.today = date.today()
        self.now = datetime.now()

    def get_special_day_info(self) -> Optional[Dict]:
        """
        Get information about today if it's a special day

        Returns:
            Dictionary with special day info, or None if regular day
        """
        month_day = (self.today.month, self.today.day)

        # Check fixed holidays
        if month_day in self.TECH_HOLIDAYS:
            return self.TECH_HOLIDAYS[month_day]

        # Check day of week patterns
        day_of_week = self.today.strftime("%A")

        # Monday motivation
        if day_of_week == "Monday" and self.today.day <= 7:
            return {
                "name": "First Monday of the Month",
                "emoji": "💪",
                "context": "fresh start",
                "type": "weekly"
            }

        # Sunday reflections
        if day_of_week == "Sunday":
            return {
                "name": "Sunday",
                "emoji": "☕",
                "context": "weekend reflection",
                "type": "weekly"
            }

        # Friday celebrations
        if day_of_week == "Friday":
            return {
                "name": "Friday",
                "emoji": "🎉",
                "context": "wrapping up the week",
                "type": "weekly"
            }

        # First day of month
        if self.today.day == 1:
            return {
                "name": f"First day of {self.today.strftime('%B')}",
                "emoji": "📅",
                "context": "new month",
                "type": "monthly"
            }

        # Last day of month
        last_day = calendar.monthrange(self.today.year, self.today.month)[1]
        if self.today.day == last_day:
            return {
                "name": f"Last day of {self.today.strftime('%B')}",
                "emoji": "📊",
                "context": "month-end reflection",
                "type": "monthly"
            }

        # Check for tech anniversaries
        tech_anniversary = self._check_tech_anniversaries()
        if tech_anniversary:
            return tech_anniversary

        return None

    def _check_tech_anniversaries(self) -> Optional[Dict]:
        """Check for notable tech anniversaries"""
        month_day = (self.today.month, self.today.day)

        tech_anniversaries = {
            (4, 1): {"name": "April Fools' Day", "emoji": "🤪", "context": "tech pranks", "type": "fun"},
            (5, 1): {"name": "May Day", "emoji": "🌸", "context": "spring renewal", "type": "minor"},
            (6, 1): {"name": "Pride Month Start", "emoji": "🏳️‍🌈", "context": "diversity in tech", "type": "major"},
        }

        return tech_anniversaries.get(month_day)

    def should_add_special_context(self) -> bool:
        """
        Determine if we should add special day context to the post

        Returns:
            True if today is special enough to mention
        """
        special_day = self.get_special_day_info()

        if not special_day:
            return False

        # Always add for major holidays
        if special_day["type"] == "major":
            return True

        # Add for tech-specific days
        if special_day["type"] == "tech":
            return True

        # Add for fun days occasionally (50% chance)
        if special_day["type"] == "fun":
            import random
            return random.random() < 0.5

        # Add for weekly/monthly milestones occasionally (30% chance)
        if special_day["type"] in ["weekly", "monthly"]:
            import random
            return random.random() < 0.3

        return False

    def get_post_context(self) -> Optional[str]:
        """
        Get contextual text to add to the post

        Returns:
            Professional context string, or None if not a special day
        """
        if not self.should_add_special_context():
            return None

        special_day = self.get_special_day_info()
        if not special_day:
            return None

        day_name = special_day["name"]
        emoji = special_day.get("emoji", "")
        context = special_day.get("context", "")
        day_type = special_day["type"]

        # Generate professional context based on day type
        if day_type == "major":
            return self._get_major_holiday_context(day_name, emoji, context)
        elif day_type == "tech":
            return self._get_tech_day_context(day_name, emoji, context)
        elif day_type == "fun":
            return self._get_fun_day_context(day_name, emoji, context)
        elif day_type == "weekly":
            return self._get_weekly_context(day_name, emoji, context)
        elif day_type == "monthly":
            return self._get_monthly_context(day_name, emoji, context)

        return None

    def _get_major_holiday_context(self, day_name: str, emoji: str, context: str) -> str:
        """Context for major holidays"""
        templates = [
            f"\n\nWishing everyone celebrating a wonderful {day_name}! {emoji}",
            f"\n\nHappy {day_name} to all! {emoji} Here's to {context} in tech and beyond.",
            f"\n\n{emoji} On this {day_name}, reflecting on {context} and growth in our field.",
        ]
        import random
        return random.choice(templates)

    def _get_tech_day_context(self, day_name: str, emoji: str, context: str) -> str:
        """Context for tech-specific days"""
        templates = [
            f"\n\n{emoji} Happy {day_name}! Perfect timing to discuss {context}.",
            f"\n\nCelebrating {day_name} today {emoji} - a great reminder of why we do what we do.",
            f"\n\n{emoji} {day_name} seemed like the perfect day to share this.",
        ]
        import random
        return random.choice(templates)

    def _get_fun_day_context(self, day_name: str, emoji: str, context: str) -> str:
        """Context for fun days"""
        templates = [
            f"\n\n{emoji} Happy {day_name}! Even in tech, we need some levity.",
            f"\n\nSince it's {day_name} {emoji}, thought I'd share something relevant.",
        ]
        import random
        return random.choice(templates)

    def _get_weekly_context(self, day_name: str, emoji: str, context: str) -> str:
        """Context for weekly milestones"""
        if "Monday" in day_name:
            return f"\n\n{emoji} Starting the week strong with some {context} energy!"
        elif "Friday" in day_name:
            return f"\n\n{emoji} Perfect Friday reflection as we're {context}."
        return None

    def _get_monthly_context(self, day_name: str, emoji: str, context: str) -> str:
        """Context for monthly milestones"""
        templates = [
            f"\n\n{emoji} As we kick off a {context}, sharing some insights.",
            f"\n\nPerfect timing for some {context} {emoji}",
        ]
        import random
        return random.choice(templates)

    def get_prompt_enhancement(self) -> Optional[str]:
        """
        Get enhancement text to add to the Gemini AI prompt

        Returns:
            String to add to prompt, or None if not special day
        """
        if not self.should_add_special_context():
            return None

        special_day = self.get_special_day_info()
        if not special_day:
            return None

        day_name = special_day["name"]
        context = special_day.get("context", "")

        return f"""
SPECIAL DAY CONTEXT:
Today is {day_name}. Consider subtly incorporating this into the post if relevant:
- You can reference "{context}" if it naturally fits the topic
- Or add a brief, professional closing line acknowledging the day
- Keep it natural and professional - don't force it if it doesn't fit
- Maximum 1-2 sentences about the special day
"""
