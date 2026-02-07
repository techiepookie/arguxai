"""GitHub API client for PR generation"""

import httpx
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.core.logging import logger
from app.models.github import FileChange, PRMetadata


class GitHubClient:
    """
    GitHub API client using personal access token (SSH token)
    
    Provides:
    - File content fetching
    - Branch creation
    - Commit creation
    - Pull request creation
    """
    
    def __init__(self):
        self.token = settings.github_token
        self.base_url = "https://api.github.com"
        
        # HTTP client with auth
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        )
    
    async def get_file_content(
        self,
        repo: str,
        file_path: str,
        branch: str = "main"
    ) -> tuple[str, str]:
        """
        Get file content from repository
        
        Args:
            repo: Repository (owner/repo)
            file_path: Path to file in repo
            branch: Branch name
            
        Returns:
            Tuple of (content, sha)
        """
        try:
            url = f"{self.base_url}/repos/{repo}/contents/{file_path}"
            params = {"ref": branch}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Decode base64 content
            content = base64.b64decode(data["content"]).decode("utf-8")
            sha = data["sha"]
            
            logger.info(
                "File content fetched",
                repo=repo,
                file_path=file_path,
                branch=branch
            )
            
            return content, sha
            
        except Exception as e:
            logger.error(
                "Failed to fetch file content",
                error=str(e),
                repo=repo,
                file_path=file_path
            )
            raise
    
    async def create_branch(
        self,
        repo: str,
        branch_name: str,
        from_branch: str = "main"
    ) -> str:
        """
        Create a new branch from existing branch
        
        Args:
            repo: Repository (owner/repo)
            branch_name: New branch name
            from_branch: Source branch
            
        Returns:
            SHA of branch HEAD
        """
        try:
            # Get SHA of from_branch
            ref_url = f"{self.base_url}/repos/{repo}/git/ref/heads/{from_branch}"
            ref_response = await self.client.get(ref_url)
            ref_response.raise_for_status()
            
            base_sha = ref_response.json()["object"]["sha"]
            
            # Create new branch
            create_url = f"{self.base_url}/repos/{repo}/git/refs"
            create_data = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha
            }
            
            create_response = await self.client.post(create_url, json=create_data)
            create_response.raise_for_status()
            
            logger.info(
                "Branch created",
                repo=repo,
                branch_name=branch_name,
                from_branch=from_branch,
                sha=base_sha
            )
            
            return base_sha
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                logger.warning(
                    "Branch already exists",
                    repo=repo,
                    branch_name=branch_name
                )
                # Branch exists, get its SHA
                existing_ref_url = f"{self.base_url}/repos/{repo}/git/ref/heads/{branch_name}"
                existing_response = await self.client.get(existing_ref_url)
                return existing_response.json()["object"]["sha"]
            raise
        except Exception as e:
            logger.error(
                "Failed to create branch",
                error=str(e),
                repo=repo,
                branch_name=branch_name
            )
            raise
    
    async def commit_changes(
        self,
        repo: str,
        branch: str,
        file_changes: List[FileChange],
        commit_message: str
    ) -> str:
        """
        Commit file changes to a branch
        
        Args:
            repo: Repository (owner/repo)
            branch: Branch to commit to
            file_changes: List of file changes
            commit_message: Commit message
            
        Returns:
            Commit SHA
        """
        try:
            # For simplicity in demo, we'll update files one by one
            # In production, use Git Tree API for atomic multi-file commits
            
            commit_sha = None
            
            for change in file_changes:
                # Get current file SHA
                try:
                    _, file_sha = await self.get_file_content(
                        repo=repo,
                        file_path=change.file_path,
                        branch=branch
                    )
                except:
                    file_sha = None  # New file
                
                # Update file
                url = f"{self.base_url}/repos/{repo}/contents/{change.file_path}"
                
                # Encode content to base64
                content_bytes = change.modified_content.encode("utf-8")
                content_b64 = base64.b64encode(content_bytes).decode("utf-8")
                
                data = {
                    "message": commit_message,
                    "content": content_b64,
                    "branch": branch
                }
                
                if file_sha:
                    data["sha"] = file_sha
                
                response = await self.client.put(url, json=data)
                response.raise_for_status()
                
                commit_sha = response.json()["commit"]["sha"]
                
                logger.info(
                    "File committed",
                    repo=repo,
                    file_path=change.file_path,
                    branch=branch,
                    commit_sha=commit_sha
                )
            
            return commit_sha
            
        except Exception as e:
            logger.error(
                "Failed to commit changes",
                error=str(e),
                repo=repo,
                branch=branch
            )
            raise
    
    async def create_pull_request(
        self,
        repo: str,
        metadata: PRMetadata
    ) -> Dict[str, Any]:
        """
        Create a pull request
        
        Args:
            repo: Repository (owner/repo)
            metadata: PR metadata
            
        Returns:
            PR data dict with url, number, etc.
        """
        try:
            url = f"{self.base_url}/repos/{repo}/pulls"
            
            data = {
                "title": metadata.title,
                "body": metadata.description,
                "head": metadata.branch_name,
                "base": metadata.base_branch
            }
            
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            
            pr_data = response.json()
            
            # Add labels if specified
            if metadata.labels:
                await self._add_labels(
                    repo=repo,
                    pr_number=pr_data["number"],
                    labels=metadata.labels
                )
            
            logger.info(
                "Pull request created",
                repo=repo,
                pr_number=pr_data["number"],
                pr_url=pr_data["html_url"]
            )
            
            return {
                "url": pr_data["html_url"],
                "number": pr_data["number"],
                "state": pr_data["state"]
            }
            
        except Exception as e:
            logger.error(
                "Failed to create pull request",
                error=str(e),
                repo=repo
            )
            raise
    
    async def _add_labels(
        self,
        repo: str,
        pr_number: int,
        labels: List[str]
    ):
        """Add labels to a pull request"""
        try:
            url = f"{self.base_url}/repos/{repo}/issues/{pr_number}/labels"
            data = {"labels": labels}
            
            await self.client.post(url, json=data)
            
            logger.info("Labels added to PR", pr_number=pr_number, labels=labels)
            
        except Exception as e:
            logger.warning("Failed to add labels", error=str(e))
    
    async def health_check(self) -> bool:
        """Check if GitHub API is accessible"""
        try:
            if not self.token:
                return False
            
            url = f"{self.base_url}/user"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error("GitHub health check failed", error=str(e))
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global GitHub client instance
github_client = GitHubClient()
