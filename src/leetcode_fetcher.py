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

    def get_easy_problems(self, limit: int = 100) -> List[Dict]:
        """Get easy problems that are free (not paid-only)"""
        all_problems = self.fetch_all_problems()
        if not all_problems:
            return []

        easy_problems = []
        for problem in all_problems:
            # Filter: Easy difficulty (level 1) and not paid-only
            if (problem.get("difficulty", {}).get("level") == 1 and
                not problem.get("paid_only", False)):

                stat = problem.get("stat", {})
                easy_problems.append({
                    "id": stat.get("frontend_question_id"),
                    "title": stat.get("question__title"),
                    "slug": stat.get("question__title_slug"),
                    "acceptance_rate": (stat.get("total_acs", 0) / max(stat.get("total_submitted", 1), 1)) * 100,
                    "total_accepted": stat.get("total_acs", 0),
                    "total_submitted": stat.get("total_submitted", 0)
                })

            if len(easy_problems) >= limit:
                break

        # Sort by acceptance rate (easier problems first)
        easy_problems.sort(key=lambda x: x["acceptance_rate"], reverse=True)
        logger.info(f"Found {len(easy_problems)} easy problems")
        return easy_problems

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
