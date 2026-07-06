# app/services/leetcode.py

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional

class LeetcodeService:
    """Service to fetch LeetCode user profile data"""
    
    LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
    
    HEADERS = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
    }
    
    def make_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GraphQL query to LeetCode"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(self.LEETCODE_GRAPHQL_URL, json=payload, headers=self.HEADERS)
        try:
            return response.json().get("data", {})
        except Exception:
            return {}
    
    def fetch_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch comprehensive LeetCode profile data for a given username"""
        queries = {
            "userPublicProfile": {
                "query": """
                    query userPublicProfile($username: String!) {
                      matchedUser(username: $username) {
                        contestBadge {
                          name
                          expired
                          hoverText
                          icon
                        }
                        username
                        githubUrl
                        twitterUrl
                        linkedinUrl
                        profile {
                          ranking
                          userAvatar
                          realName
                          aboutMe
                          school
                          websites
                          countryName
                          company
                          jobTitle
                          skillTags
                          postViewCount
                          postViewCountDiff
                          reputation
                          reputationDiff
                          solutionCount
                          solutionCountDiff
                          categoryDiscussCount
                          categoryDiscussCountDiff
                        }
                      }
                    }
                """,
                "variables": {"username": username}
            },
            "languageStats": {
                "query": """
                    query languageStats($username: String!) {
                      matchedUser(username: $username) {
                        languageProblemCount {
                          languageName
                          problemsSolved
                        }
                      }
                    }
                """,
                "variables": {"username": username}
            },
            "skillStats": {
                "query": """
                    query skillStats($username: String!) {
                      matchedUser(username: $username) {
                        tagProblemCounts {
                          advanced {
                            tagName
                            tagSlug
                            problemsSolved
                          }
                          intermediate {
                            tagName
                            tagSlug
                            problemsSolved
                          }
                          fundamental {
                            tagName
                            tagSlug
                            problemsSolved
                          }
                        }
                      }
                    }
                """,
                "variables": {"username": username}
            },
            "userProblemsSolved": {
                "query": """
                    query userProblemsSolved($username: String!) {
                      matchedUser(username: $username) {
                        problemsSolvedBeatsStats {
                          difficulty
                          percentage
                        }
                        submitStatsGlobal {
                          acSubmissionNum {
                            difficulty
                            count
                          }
                        }
                      }
                    }
                """,
                "variables": {"username": username}
            },
            "userProfileCalendar": {
                "query": """
                    query userProfileCalendar($username: String!, $year: Int) {
                      matchedUser(username: $username) {
                        userCalendar(year: $year) {
                          activeYears
                          streak
                          totalActiveDays
                          dccBadges {
                            timestamp
                            badge {
                              name
                              icon
                            }
                          }
                          submissionCalendar
                        }
                      }
                    }
                """,
                "variables": {"username": username, "year": datetime.now().year}
            },
            "getStreakCounter": {
                "query": """
                    query getStreakCounter {
                      streakCounter {
                        streakCount
                        daysSkipped
                        currentDayCompleted
                      }
                    }
                """
            },
            "currentTimestamp": {
                "query": "query currentTimestamp { currentTimestamp }"
            },
        }

        results = {}
        for key, q in queries.items():
            results[key] = self.make_query(q["query"], q.get("variables"))

        return results
