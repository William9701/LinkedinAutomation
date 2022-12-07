import json
import random
from typing import Dict, List, Optional
from pathlib import Path


class TopicManager:
    """Manages topics for LinkedIn posts"""

    def __init__(self, topics_file: str = "topics.json"):
        self.topics_file = Path(topics_file)
        self.topics = self._load_topics()

    def _load_topics(self) -> Dict:
        """Load topics from JSON file"""
        if not self.topics_file.exists():
            return {"topics": []}

        with open(self.topics_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_topics(self) -> None:
        """Save topics back to JSON file"""
        with open(self.topics_file, "w", encoding="utf-8") as f:
            json.dump(self.topics, f, indent=2, ensure_ascii=False)

    def get_unused_topic(self) -> Optional[Dict]:
        """Get a random unused topic"""
        unused_topics = [t for t in self.topics["topics"] if not t.get("used", False)]

        if not unused_topics:
            # Reset all topics if all have been used
            for topic in self.topics["topics"]:
                topic["used"] = False
            self._save_topics()
            unused_topics = self.topics["topics"]

        if not unused_topics:
            return None

        topic = random.choice(unused_topics)
        return topic

    def mark_topic_used(self, topic_id: int) -> None:
        """Mark a topic as used"""
        for topic in self.topics["topics"]:
            if topic["id"] == topic_id:
                topic["used"] = True
                break
        self._save_topics()

    def add_topic(self, category: str, title: str, prompt: str) -> None:
        """Add a new topic"""
        new_id = max([t["id"] for t in self.topics["topics"]], default=0) + 1
        new_topic = {
            "id": new_id,
            "category": category,
            "title": title,
            "prompt": prompt,
            "used": False
        }
        self.topics["topics"].append(new_topic)
        self._save_topics()

    def get_all_topics(self) -> List[Dict]:
        """Get all topics"""
        return self.topics["topics"]

    def reset_all_topics(self) -> None:
        """Reset all topics to unused"""
        for topic in self.topics["topics"]:
            topic["used"] = False
        self._save_topics()
