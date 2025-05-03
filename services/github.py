import requests
import json
from datetime import datetime, timedelta
from collections import Counter
import base64
import os
from typing import Dict, List, Optional, Any

class GitHubJobInsights:
    """A GitHub integration that extracts actionable insights for job matching."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token=None):
        """Initialize with an optional GitHub token."""
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Job-Insights"
        }
        # GraphQL requires a token, so we'll provide clear messaging if using those endpoints
        if token:
            self.headers["Authorization"] = f"token {token}"
            self.can_use_graphql = True
        else:
            self.can_use_graphql = False

        # Track rate limit
        self.rate_limit = None
        self.rate_remaining = None

    def _update_rate_limit(self, response):
        """Update rate limit information from response headers."""
        if 'X-RateLimit-Limit' in response.headers:
            self.rate_limit = response.headers['X-RateLimit-Limit']
            self.rate_remaining = response.headers['X-RateLimit-Remaining']

    def get_user_data(self, username):
        """Fetch basic user profile data."""
        url = f"{self.BASE_URL}/users/{username}"
        response = requests.get(url, headers=self.headers)
        self._update_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            return None

    def get_user_repos(self, username):
        """Fetch all repositories for a user with enough details for analysis."""
        # Request more details per repo to minimize API calls
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {"sort": "updated", "direction": "desc", "per_page": 100}
        all_repos = []
        page = 1

        # Pagination handling
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            self._update_rate_limit(response)

            if response.status_code != 200:
                break

            repos = response.json()
            all_repos.extend(repos)

            if len(repos) < 100:  # Last page
                break

            page += 1

        return all_repos

    def get_repo_languages(self, repo_full_name):
        """Fetch languages used in a repository."""
        url = f"{self.BASE_URL}/repos/{repo_full_name}/languages"
        response = requests.get(url, headers=self.headers)
        self._update_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def get_repo_readme(self, repo_full_name):
        """Fetch README content for a repository."""
        url = f"{self.BASE_URL}/repos/{repo_full_name}/readme"
        response = requests.get(url, headers=self.headers)
        self._update_rate_limit(response)

        if response.status_code == 200:
            data = response.json()
            try:
                # README content is base64 encoded
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
            except:
                return None
        return None

    def get_repo_commits(self, repo_full_name, days=90):
        """Get recent commits for a repository."""
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"{self.BASE_URL}/repos/{repo_full_name}/commits"
        params = {"since": since_date, "per_page": 100}  # Limit to last 100 commits in the period

        response = requests.get(url, headers=self.headers, params=params)
        self._update_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        return []

    def get_user_contributions(self, username):
        """Get user's PRs and issues on other repositories (requires GraphQL)."""
        if not self.can_use_graphql:
            return {"pull_requests": [], "issues": []}

        # The GraphQL query to fetch user's contributions
        query = """
        query($username: String!, $from: DateTime!) {
          user(login: $username) {
            contributionsCollection(from: $from) {
              pullRequestContributions(first: 100) {
                nodes {
                  pullRequest {
                    title
                    url
                    repository { nameWithOwner }
                    state
                  }
                }
              }
              issueContributions(first: 100) {
                nodes {
                  issue {
                    title
                    url
                    repository { nameWithOwner }
                    state
                  }
                }
              }
            }
          }
        }
        """

        # Get contributions from the last year
        from_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
        variables = {
            "username": username,
            "from": from_date
        }

        url = "https://api.github.com/graphql"
        response = requests.post(
            url,
            headers=self.headers,
            json={"query": query, "variables": variables}
        )

        contributions = {"pull_requests": [], "issues": []}

        if response.status_code == 200:
            data = response.json()
            try:
                user_data = data.get("data", {}).get("user", {})
                collections = user_data.get("contributionsCollection", {})

                # Extract PRs
                pr_nodes = collections.get("pullRequestContributions", {}).get("nodes", [])
                for node in pr_nodes:
                    pr = node.get("pullRequest", {})
                    if pr and pr.get("repository", {}).get("nameWithOwner", "").split("/")[0] != username:
                        contributions["pull_requests"].append({
                            "title": pr.get("title"),
                            "url": pr.get("url"),
                            "repo": pr.get("repository", {}).get("nameWithOwner"),
                            "state": pr.get("state")
                        })

                # Extract issues
                issue_nodes = collections.get("issueContributions", {}).get("nodes", [])
                for node in issue_nodes:
                    issue = node.get("issue", {})
                    if issue and issue.get("repository", {}).get("nameWithOwner", "").split("/")[0] != username:
                        contributions["issues"].append({
                            "title": issue.get("title"),
                            "url": issue.get("url"),
                            "repo": issue.get("repository", {}).get("nameWithOwner"),
                            "state": issue.get("state")
                        })
            except Exception:
                pass

        return contributions

    def get_starred_repos(self, username, max_pages=3):
        """Get user's starred repositories (limited to reduce API calls)."""
        url = f"{self.BASE_URL}/users/{username}/starred"
        params = {"per_page": 100}  # Get 100 per page
        starred = []

        for page in range(1, max_pages + 1):
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            self._update_rate_limit(response)

            if response.status_code != 200:
                break

            page_starred = response.json()
            starred.extend(page_starred)

            if len(page_starred) < 100:  # Last page
                break

        return starred

    def extract_job_insights(self, username):
        """Extract actionable insights for job matching from a user's GitHub data."""
        # Get basic user data
        user_data = self.get_user_data(username)
        if not user_data:
            return None

        # Initialize insights structure
        insights = {
            "basic_info": {
                "username": username,
                "name": user_data.get("name"),
                "company": user_data.get("company"),
                "blog": user_data.get("blog"),
                "bio": user_data.get("bio"),
                "public_repos": user_data.get("public_repos", 0)
            },
            "top_languages": {},
            "personal_projects": [],
            "forked_repos": [],
            "most_active_repos": [],
            "repo_topics": [],
            "open_source_contributions": {
                "pull_requests": [],
                "issues": []
            },
            "contribution_activity": {
                "last_90_days": 0,
                "last_30_days": 0
            },
            "tech_preferences": {
                "from_starred": [],
                "from_readme": []
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "with_token": self.can_use_graphql
            }
        }

        # Get all repos to analyze
        repos = self.get_user_repos(username)

        # Track languages across all repos
        language_counter = Counter()
        readme_keywords = set()
        topics_counter = Counter()

        # Track commit activity
        commit_counts = {
            "last_30_days": 0,
            "last_90_days": 0
        }

        # Repositories to analyze in detail
        # Limit to 10 most recently updated repos to avoid rate limiting
        repos_to_analyze = sorted(repos, key=lambda r: r.get("updated_at", ""), reverse=True)[:10]

        for repo in repos:
            # Separate personal projects vs forks
            repo_item = {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "updated_at": repo.get("updated_at")
            }

            # Track topics/tags
            if repo.get("topics"):
                for topic in repo.get("topics", []):
                    topics_counter[topic] += 1

            # Only count non-forked repos for languages and personal projects
            if not repo.get("fork"):
                insights["personal_projects"].append(repo_item)

                # Get detailed language breakdown for own repos
                # (only for the most recently updated repos to avoid rate limiting)
                if repo in repos_to_analyze:
                    languages = self.get_repo_languages(repo.get("full_name"))
                    for lang, bytes_count in languages.items():
                        language_counter[lang] += bytes_count

                    # Get README for keyword extraction (also limited to avoid rate limits)
                    readme = self.get_repo_readme(repo.get("full_name"))
                    if readme:
                        # Extract potential technologies from README
                        common_tech_keywords = [
                            "javascript", "python", "java", "golang", "c#", "typescript",
                            "react", "vue", "angular", "node", "django", "flask", "spring",
                            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
                            "sql", "nosql", "mongodb", "postgresql", "mysql", "redis"
                        ]
                        for keyword in common_tech_keywords:
                            if keyword.lower() in readme.lower():
                                readme_keywords.add(keyword.lower())

                    # Get recent commit activity
                    if repo in repos_to_analyze[:5]:  # Limit to 5 most recent repos
                        commits = self.get_repo_commits(repo.get("full_name"), days=90)

                        for commit in commits:
                            commit_date = commit.get("commit", {}).get("author", {}).get("date", "")
                            if commit_date:
                                commit_date = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
                                days_ago = (datetime.now() - commit_date).days

                                if days_ago <= 90:
                                    commit_counts["last_90_days"] += 1

                                    if days_ago <= 30:
                                        commit_counts["last_30_days"] += 1

            else:
                insights["forked_repos"].append(repo_item)

        # Set most active repositories based on recent commits
        insights["most_active_repos"] = sorted(
            [r for r in repos if not r.get("fork")],
            key=lambda r: r.get("updated_at", ""),
            reverse=True
        )[:5]  # Top 5 most recently updated

        # Convert most active repos to the same format
        insights["most_active_repos"] = [
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
                "updated_at": repo.get("updated_at")
            }
            for repo in insights["most_active_repos"]
        ]

        # Set top languages (sort by bytes of code)
        insights["top_languages"] = {
            lang: count for lang, count in sorted(
                language_counter.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 languages
        }

        # Set repository topics
        insights["repo_topics"] = [
            {"topic": topic, "count": count}
            for topic, count in topics_counter.most_common(15)
        ]

        # Set contribution activity
        insights["contribution_activity"]["last_90_days"] = commit_counts["last_90_days"]
        insights["contribution_activity"]["last_30_days"] = commit_counts["last_30_days"]

        # Set tech preferences from README analysis
        insights["tech_preferences"]["from_readme"] = sorted(list(readme_keywords))

        # Get starred repositories for tech preferences (limited to reduce API calls)
        starred_repos = self.get_starred_repos(username)

        # Extract technology preferences from starred repos
        starred_langs = Counter()
        starred_topics = Counter()

        for repo in starred_repos:
            if repo.get("language"):
                starred_langs[repo.get("language")] += 1

            # Count topics from starred repos
            for topic in repo.get("topics", []):
                starred_topics[topic] += 1

        insights["tech_preferences"]["from_starred"] = [
            {"language": lang, "count": count}
            for lang, count in starred_langs.most_common(10)
        ] + [
            {"topic": topic, "count": count}
            for topic, count in starred_topics.most_common(10)
        ]

        # Get open source contributions (PRs and issues on others' repos)
        if self.can_use_graphql:
            contributions = self.get_user_contributions(username)
            insights["open_source_contributions"] = contributions

        return insights


def get_github_insights(username: str) -> Dict[str, Any]:
    """
    Function to get GitHub insights for a given username.
    Can be used by the API routes.
    """
    # Get token from environment variables
    token = os.environ.get("GITHUB_TOKEN")
    
    # Initialize the insights class
    insights_client = GitHubJobInsights(token)
    
    # Extract and return insights
    return insights_client.extract_job_insights(username)