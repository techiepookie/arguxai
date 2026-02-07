"""Jira API client for issue tracking"""

import httpx
import base64
from typing import Dict, Any, Optional, List
from app.config import settings
from app.core.logging import logger
from app.models.jira import JiraIssue, JiraIssueCreate


class JiraClient:
    """
    Jira REST API client
    
    Provides:
    - Issue creation
    - Issue assignment
    - Status updates
    - Comment posting
    
    Authentication: Basic Auth with email + API token
    """
    
    def __init__(self):
        self.domain = settings.jira_domain  # e.g., "yourcompany.atlassian.net"
        self.email = settings.jira_email
        self.api_token = settings.jira_api_token
        
        # Build base URL
        self.base_url = f"https://{self.domain}/rest/api/3" if self.domain else None
        
        # Create auth header
        if self.email and self.api_token:
            auth_string = f"{self.email}:{self.api_token}"
            auth_bytes = auth_string.encode('utf-8')
            auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
            
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Basic {auth_b64}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
        else:
            self.client = httpx.AsyncClient(timeout=30.0)
    
    async def create_issue(
        self,
        issue_data: JiraIssueCreate
    ) -> JiraIssue:
        """
        Create a Jira issue
        
        Args:
            issue_data: Issue details
            
        Returns:
            Created Jira issue
        """
        try:
            if not self.base_url:
                raise ValueError("Jira domain not configured")
            
            url = f"{self.base_url}/issue"
            
            # Build Jira payload
            payload = {
                "fields": {
                    "project": {
                        "key": issue_data.project_key
                    },
                    "summary": issue_data.summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": issue_data.description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {
                        "name": "Task"  # Use Task instead of Bug
                    },
                    "priority": {
                        "name": issue_data.priority.value
                    }
                }
            }
            
            # Add assignee if provided (skip if it causes errors)
            # if issue_data.assignee:
            #     payload["fields"]["assignee"] = {
            #         "emailAddress": issue_data.assignee
            #     }
            
            # Add labels
            if issue_data.labels:
                payload["fields"]["labels"] = issue_data.labels
            
            # Add components (skip if they don't exist in project)
            # if issue_data.components:
            #     payload["fields"]["components"] = [
            #         {"name": comp} for comp in issue_data.components
            #     ]
            
            # Create issue
            response = await self.client.post(url, json=payload)
            
            # Log the error details if it fails
            if response.status_code != 201:
                error_detail = response.text
                logger.error(
                    "Jira API error",
                    status=response.status_code,
                    error=error_detail,
                    payload=payload
                )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Extract issue details
            issue_key = data.get("key")
            issue_id = data.get("id")
            issue_url = f"https://{self.domain}/browse/{issue_key}"
            
            logger.info(
                "Jira issue created",
                key=issue_key,
                url=issue_url
            )
            
            # Get full issue details
            issue = await self.get_issue(issue_key)
            
            return issue
            
        except Exception as e:
            logger.error("Failed to create Jira issue", error=str(e))
            raise
    
    async def get_issue(self, issue_key: str) -> JiraIssue:
        """
        Get Jira issue details
        
        Args:
            issue_key: Issue key (e.g., 'CONV-123')
            
        Returns:
            Jira issue details
        """
        try:
            url = f"{self.base_url}/issue/{issue_key}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract fields
            fields = data.get("fields", {})
            assignee_data = fields.get("assignee", {})
            assignee_name = assignee_data.get("displayName") if assignee_data else None
            
            issue = JiraIssue(
                key=data.get("key"),
                id=data.get("id"),
                url=f"https://{self.domain}/browse/{data.get('key')}",
                summary=fields.get("summary", ""),
                status=fields.get("status", {}).get("name", "Unknown"),
                assignee=assignee_name
            )
            
            return issue
            
        except Exception as e:
            logger.error("Failed to get Jira issue", error=str(e), key=issue_key)
            raise
    
    async def add_comment(
        self,
        issue_key: str,
        comment: str
    ) -> Dict[str, Any]:
        """
        Add comment to Jira issue
        
        Args:
            issue_key: Issue key
            comment: Comment text
            
        Returns:
            Comment data
        """
        try:
            url = f"{self.base_url}/issue/{issue_key}/comment"
            
            payload = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment
                                }
                            ]
                        }
                    ]
                }
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info("Comment added to Jira", key=issue_key)
            
            return response.json()
            
        except Exception as e:
            logger.error("Failed to add comment", error=str(e))
            raise
    
    async def transition_issue(
        self,
        issue_key: str,
        transition_name: str
    ) -> None:
        """
        Transition issue to new status
        
        Args:
            issue_key: Issue key
            transition_name: Target status (e.g., 'In Progress', 'Done')
        """
        try:
            # Get available transitions
            transitions_url = f"{self.base_url}/issue/{issue_key}/transitions"
            response = await self.client.get(transitions_url)
            response.raise_for_status()
            
            transitions = response.json().get("transitions", [])
            
            # Find matching transition
            transition_id = None
            for trans in transitions:
                if trans.get("name", "").lower() == transition_name.lower():
                    transition_id = trans.get("id")
                    break
            
            if not transition_id:
                logger.warning(
                    "Transition not found",
                    key=issue_key,
                    transition=transition_name
                )
                return
            
            # Execute transition
            payload = {
                "transition": {
                    "id": transition_id
                }
            }
            
            response = await self.client.post(transitions_url, json=payload)
            response.raise_for_status()
            
            logger.info(
                "Issue transitioned",
                key=issue_key,
                status=transition_name
            )
            
        except Exception as e:
            logger.error("Failed to transition issue", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check if Jira API is accessible"""
        try:
            if not self.base_url or not self.email or not self.api_token:
                return False
            
            # Simple API call to verify credentials
            url = f"{self.base_url}/myself"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error("Jira health check failed", error=str(e))
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global Jira client instance
jira_client = JiraClient()
