from crewai.tools import BaseTool
import os
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

class GithubProfileFetcher(BaseTool):
    name: str = "github_profile_fetcher"  # ✅ Added type annotations
    description: str = "Fetches public GitHub profile and repo details from any username"

    def _run(self, github_url: str):
        username = github_url.strip("/").split("/")[-1]
        gh_token = os.getenv("GH_TOKEN")
        headers = {"Authorization": f"token {gh_token}"} if gh_token else {}

        # Fetch profile info
        profile = requests.get(f"https://api.github.com/users/{username}", headers=headers).json()

        # Fetch repos
        repos = requests.get(
            f"https://api.github.com/users/{username}/repos",
            headers=headers,
            params={"per_page": 100}
        ).json()

        return {
            "profile": profile,
            "repos": [
                {
                    "name": r.get("name"),
                    "description": r.get("description"),
                    "language": r.get("language"),
                    "stars": r.get("stargazers_count")
                }
                for r in repos if isinstance(r, dict)
            ]
        }

if __name__ == "__main__":
    tool = GithubProfileFetcher()
    result = tool.run("https://github.com/AmartyaGhoshyoo")  # Example user
    console=Console()
    print(result)
