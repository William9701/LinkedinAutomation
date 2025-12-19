import requests
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class LeetCodeFetcher:
    """Fetches LeetCode problems for content generation"""

    def __init__(self):
        self.api_url = "https://leetcode.com/api/problems/all/"
        self.graphql_url = "https://leetcode.com/graphql"

    def fetch_all_problems(self) -> Optional[List[Dict]]:
        """Fetch all problems from LeetCode API"""
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("stat_status_pairs", [])
            else:
                logger.error(f"Failed to fetch problems: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching problems: {str(e)}")
            return None

    def get_problems_by_difficulty(self, difficulty_level: int = None, limit: int = 100) -> List[Dict]:
        """
        Get problems filtered by difficulty

        Args:
            difficulty_level: 1 (Easy), 2 (Medium), 3 (Hard), None (All)
            limit: Max number of problems to return

        Returns:
            List of problem dictionaries
        """
        all_problems = self.fetch_all_problems()
        if not all_problems:
            return []

        filtered_problems = []
        difficulty_map = {1: "Easy", 2: "Medium", 3: "Hard"}

        for problem in all_problems:
            # Filter: Not paid-only
            if problem.get("paid_only", False):
                continue

            level = problem.get("difficulty", {}).get("level")

            # Filter by difficulty if specified
            if difficulty_level is not None and level != difficulty_level:
                continue

            stat = problem.get("stat", {})
            filtered_problems.append({
                "id": stat.get("frontend_question_id"),
                "title": stat.get("question__title"),
                "slug": stat.get("question__title_slug"),
                "difficulty": difficulty_map.get(level, "Unknown"),
                "difficulty_level": level,
                "acceptance_rate": (stat.get("total_acs", 0) / max(stat.get("total_submitted", 1), 1)) * 100,
                "total_accepted": stat.get("total_acs", 0),
                "total_submitted": stat.get("total_submitted", 0)
            })

            if len(filtered_problems) >= limit:
                break

        # Sort by acceptance rate
        filtered_problems.sort(key=lambda x: x["acceptance_rate"], reverse=True)

        diff_name = difficulty_map.get(difficulty_level, "All") if difficulty_level else "All"
        logger.info(f"Found {len(filtered_problems)} {diff_name} problems")
        return filtered_problems

    def get_easy_problems(self, limit: int = 100) -> List[Dict]:
        """Get easy problems (difficulty level 1)"""
        return self.get_problems_by_difficulty(1, limit)

    def get_medium_problems(self, limit: int = 100) -> List[Dict]:
        """Get medium problems (difficulty level 2)"""
        return self.get_problems_by_difficulty(2, limit)

    def get_hard_problems(self, limit: int = 100) -> List[Dict]:
        """Get hard problems (difficulty level 3)"""
        return self.get_problems_by_difficulty(3, limit)

    def get_all_difficulties(self, easy_count: int = 100, medium_count: int = 50, hard_count: int = 30) -> List[Dict]:
        """Get mixed difficulties"""
        all_problems = []
        all_problems.extend(self.get_easy_problems(easy_count))
        all_problems.extend(self.get_medium_problems(medium_count))
        all_problems.extend(self.get_hard_problems(hard_count))

        logger.info(f"Total problems fetched: {len(all_problems)} (Easy: {easy_count}, Medium: {medium_count}, Hard: {hard_count})")
        return all_problems

    def get_problem_details(self, title_slug: str) -> Optional[Dict]:
        """Get detailed problem description using GraphQL"""
        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                title
                content
                difficulty
                exampleTestcases
                topicTags {
                    name
                }
                hints
                codeSnippets {
                    lang
                    code
                }
            }
        }
        """

        try:
            response = requests.post(
                self.graphql_url,
                json={
                    "query": query,
                    "variables": {"titleSlug": title_slug}
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("question")
            else:
                logger.error(f"Failed to fetch problem details: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching problem details: {str(e)}")
            return None

    def save_easy_problems_to_file(self, filename: str = "leetcode_easy_problems.json"):
        """Save easy problems to a JSON file for quick access"""
        problems = self.get_easy_problems(limit=200)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(problems, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(problems)} problems to {filename}")
            return len(problems)
        except Exception as e:
            logger.error(f"Error saving problems: {str(e)}")
            return 0


if __name__ == "__main__":
    # Test the fetcher
    logging.basicConfig(level=logging.INFO)
    fetcher = LeetCodeFetcher()

    # Save easy problems
    count = fetcher.save_easy_problems_to_file()
    print(f"Saved {count} easy LeetCode problems")

    # Test getting details for one problem
    problems = fetcher.get_easy_problems(limit=1)
    if problems:
        problem = problems[0]
        print(f"\nTesting problem: {problem['title']}")
        details = fetcher.get_problem_details(problem['slug'])
        if details:
            print(f"Description length: {len(details.get('content', ''))}")
            print(f"Hints: {len(details.get('hints', []))}")
