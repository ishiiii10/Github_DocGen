from github import Github
from flask import current_app
import re
from typing import Dict, Any, List
import base64

class GitHubService:
    def __init__(self):
        self.github = Github(current_app.config['GITHUB_TOKEN'])
        
    def _extract_repo_info(self, url: str) -> tuple:
        """Extract owner and repo name from GitHub URL."""
        pattern = r'github\.com/([^/]+)/([^/]+)'
        match = re.search(pattern, url)
        if not match:
            raise ValueError("Invalid GitHub repository URL")
        return match.group(1), match.group(2)
        
    def fetch_repository(self, repo_url: str) -> Dict[str, Any]:
        """Fetch repository data from GitHub."""
        owner, repo_name = self._extract_repo_info(repo_url)
        repo = self.github.get_repo(f"{owner}/{repo_name}")
        
        # Get repository details
        repo_data = {
            'name': repo.name,
            'description': repo.description,
            'owner': repo.owner.login,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'language': repo.language,
            'topics': repo.get_topics(),
            'created_at': repo.created_at.isoformat(),
            'updated_at': repo.updated_at.isoformat(),
            'files': self._get_repository_files(repo),
            'readme': self._get_readme_content(repo)
        }
        
        return repo_data
        
    def _get_repository_files(self, repo) -> List[Dict[str, Any]]:
        """Get all files in the repository."""
        files = []
        contents = repo.get_contents("")
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                files.append({
                    'path': file_content.path,
                    'size': file_content.size,
                    'type': file_content.type
                })
                
        return files
        
    def _get_readme_content(self, repo) -> str:
        """Get README content if it exists."""
        try:
            readme = repo.get_readme()
            return base64.b64decode(readme.content).decode('utf-8')
        except:
            return "" 