"""GitHub PR generation API endpoints"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.models.github import PRGenerationRequest, PRGenerationResponse
from app.services.pr_generator import pr_generator
from app.core.dependencies import APIKeyDep
from app.core.logging import logger

router = APIRouter()


@router.post("/generate-pr", response_model=PRGenerationResponse)
async def generate_pull_request(
    request: PRGenerationRequest,
    api_key: APIKeyDep = None
) -> PRGenerationResponse:
    """
    Generate a pull request with AI-powered code fixes
    
    **Workflow**:
    1. Fetch diagnosed issue
    2. Get code context from GitHub repository
    3. Generate code fixes using DeepSeek AI
    4. Create feature branch
    5. Commit changes with detailed message
    6. Create pull request with comprehensive description
    7. Update issue with PR information
    
    **Requirements**:
    - Issue must be diagnosed (have AI diagnosis)
    - GitHub token must be configured
    - Repository must be accessible
    
    **Example Request**:
    ```json
    {
      "issue_id": "issue_1707289800_otpverification",
      "repository": "your-org/your-repo",
      "target_files": ["services/otp_service.py", "config/twilio.py"],
      "base_branch": "main"
    }
    ```
    
    **Returns**: PR details with URL, number, commit SHA
    """
    try:
        logger.info(
            "PR generation request",
            issue_id=request.issue_id,
            repository=request.repository,
            files=len(request.target_files)
        )
        
        response = await pr_generator.generate_pr(
            issue_id=request.issue_id,
            repository=request.repository,
            target_files=request.target_files,
            base_branch=request.base_branch or "main"
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("PR generation endpoint error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PR: {str(e)}"
        )


@router.post("/generate-pr-simple", response_model=PRGenerationResponse)
async def generate_pr_simple(
    issue_id: str = Query(..., description="Issue ID"),
    repository: str = Query(..., description="GitHub repository (owner/repo)"),
    file_path: str = Query(..., description="File to fix"),
    api_key: APIKeyDep = None
) -> PRGenerationResponse:
    """
    Simplified PR generation endpoint for single file fixes
    
    **Example**:
    ```
    POST /api/github/generate-pr-simple?issue_id=issue_123&repository=org/repo&file_path=services/otp.py
    ```
    
    **Use Case**: Quick fixes for single-file issues
    """
    try:
        request = PRGenerationRequest(
            issue_id=issue_id,
            repository=repository,
            target_files=[file_path],
            base_branch="main"
        )
        
        response = await pr_generator.generate_pr(
            issue_id=request.issue_id,
            repository=request.repository,
            target_files=request.target_files,
            base_branch=request.base_branch
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Simple PR generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PR: {str(e)}"
        )


@router.get("/prs")
async def list_pull_requests(
    repository: str = Query(default="techiepookie/demo-login-app", description="GitHub repository (owner/repo)"),
    api_key: APIKeyDep = None
):
    """
    List all pull requests from the repository
    
    **Example**:
    ```
    GET /api/github/prs?repository=techiepookie/demo-login-app
    ```
    """
    try:
        from app.integrations.github_client import github_client
        
        url = f"https://api.github.com/repos/{repository}/pulls"
        response = await github_client.client.get(url)
        response.raise_for_status()
        
        prs = response.json()
        
        # Format PR data
        formatted_prs = []
        for pr in prs:
            formatted_prs.append({
                "number": pr["number"],
                "title": pr["title"],
                "url": pr["html_url"],
                "state": pr["state"],
                "branch": pr["head"]["ref"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "user": pr["user"]["login"]
            })
        
        logger.info("PRs listed", repository=repository, count=len(formatted_prs))
        return {"prs": formatted_prs, "count": len(formatted_prs)}
        
    except Exception as e:
        logger.error("Failed to list PRs", error=str(e), repository=repository)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list PRs: {str(e)}"
        )


@router.get("/prs/{pr_number}")
async def get_pull_request_details(
    pr_number: int,
    repository: str = Query(default="techiepookie/demo-login-app", description="GitHub repository (owner/repo)"),
    api_key: APIKeyDep = None
):
    """
    Get detailed information about a specific pull request
    
    **Example**:
    ```
    GET /api/github/prs/1?repository=techiepookie/demo-login-app
    ```
    """
    try:
        from app.integrations.github_client import github_client
        
        # Get PR details
        pr_url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}"
        pr_response = await github_client.client.get(pr_url)
        pr_response.raise_for_status()
        pr_data = pr_response.json()
        
        # Get PR files
        files_url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}/files"
        files_response = await github_client.client.get(files_url)
        files_response.raise_for_status()
        files_data = files_response.json()
        
        # Get PR commits
        commits_url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}/commits"
        commits_response = await github_client.client.get(commits_url)
        commits_response.raise_for_status()
        commits_data = commits_response.json()
        
        # Format response
        result = {
            "number": pr_data["number"],
            "title": pr_data["title"],
            "body": pr_data["body"],
            "state": pr_data["state"],
            "url": pr_data["html_url"],
            "branch": pr_data["head"]["ref"],
            "base_branch": pr_data["base"]["ref"],
            "created_at": pr_data["created_at"],
            "updated_at": pr_data["updated_at"],
            "merged_at": pr_data.get("merged_at"),
            "user": {
                "login": pr_data["user"]["login"],
                "avatar_url": pr_data["user"]["avatar_url"]
            },
            "additions": pr_data["additions"],
            "deletions": pr_data["deletions"],
            "changed_files": pr_data["changed_files"],
            "commits": len(commits_data),
            "files": [
                {
                    "filename": f["filename"],
                    "status": f["status"],
                    "additions": f["additions"],
                    "deletions": f["deletions"],
                    "changes": f["changes"],
                    "patch": f.get("patch", "")
                }
                for f in files_data
            ],
            "commit_messages": [
                {
                    "sha": c["sha"][:7],
                    "message": c["commit"]["message"],
                    "author": c["commit"]["author"]["name"],
                    "date": c["commit"]["author"]["date"]
                }
                for c in commits_data
            ]
        }
        
        logger.info("PR details fetched", pr_number=pr_number, repository=repository)
        return result
        
    except Exception as e:
        logger.error("Failed to get PR details", error=str(e), pr_number=pr_number)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get PR details: {str(e)}"
        )
