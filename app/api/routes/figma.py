"""Figma design review API endpoints"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from app.models.figma import FigmaReviewRequest, FigmaReviewResponse, DesignAnalysis
from app.services.figma_review_service import figma_review_service
from app.core.dependencies import APIKeyDep
from app.core.logging import logger

router = APIRouter()


@router.post("/review", response_model=FigmaReviewResponse)
async def review_figma_design(
    request: FigmaReviewRequest,
    post_comments: bool = Query(False, description="Post analysis as Figma comments"),
    api_key: APIKeyDep = None
) -> FigmaReviewResponse:
    """
    Review Figma design using DeepSeek Vision AI
    
    **Workflow**:
    1. Fetch Figma file and frames
    2. Render frame screenshots (PNG)
    3. Analyze with DeepSeek Vision for conversion issues
    4. Optionally post analysis as Figma comments
    5. Return comprehensive design analysis
    
    **AI Analysis Focuses On**:
    - Visual hierarchy (is CTA clear?)
    - Contrast & readability
    - Cognitive load
    - Trust signals
    - Mobile optimization
    - Error states
    
    **Example Request**:
    ```json
    {
      "file_key": "abc123def456",
      "frame_ids": ["123:456", "123:789"],
      "issue_id": "issue_1707289800_otpverification"
    }
    ```
    
    **Returns**: Design analysis with issues, recommendations, and conversion impact assessment
    """
    try:
        logger.info(
            "Figma review request",
            file_key=request.file_key,
            frames=len(request.frame_ids) if request.frame_ids else "all"
        )
        
        # Build issue context if provided
        issue_context = None
        if request.issue_id:
            from app.services.issue_manager import issue_manager
            issue = issue_manager.get_issue(request.issue_id)
            if issue:
                issue_context = f"Conversion issue: {issue.anomaly.funnel_step} dropped {issue.anomaly.drop_percentage:.1f}%"
        
        # Perform design review
        analyses = await figma_review_service.review_design(
            file_key=request.file_key,
            frame_ids=request.frame_ids,
            issue_context=issue_context
        )
        
        # Optionally post comments
        if post_comments:
            await figma_review_service.post_analysis_as_comments(
                file_key=request.file_key,
                analyses=analyses
            )
            logger.info("Analysis posted as Figma comments")
        
        return FigmaReviewResponse(
            success=True,
            file_key=request.file_key,
            frames_analyzed=len(analyses),
            analyses=analyses,
            message=f"Analyzed {len(analyses)} frames successfully"
        )
        
    except Exception as e:
        logger.error("Figma review failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Design review failed: {str(e)}"
        )


@router.post("/review-simple", response_model=FigmaReviewResponse)
async def review_figma_simple(
    file_key: str = Query(..., description="Figma file key"),
    frame_id: Optional[str] = Query(None, description="Specific frame ID"),
    api_key: APIKeyDep = None
) -> FigmaReviewResponse:
    """
    Simplified Figma review endpoint
    
    **Example**:
    ```
    POST /api/figma/review-simple?file_key=abc123&frame_id=123:456
    ```
    
    **Use Case**: Quick single-frame analysis
    """
    try:
        frame_ids = [frame_id] if frame_id else None
        
        analyses = await figma_review_service.review_design(
            file_key=file_key,
            frame_ids=frame_ids
        )
        
        return FigmaReviewResponse(
            success=True,
            file_key=file_key,
            frames_analyzed=len(analyses),
            analyses=analyses,
            message="Design review completed"
        )
        
    except Exception as e:
        logger.error("Simple Figma review failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Review failed: {str(e)}"
        )


@router.get("/analysis/{file_key}")
async def get_design_analysis(
    file_key: str,
    api_key: APIKeyDep = None
) -> Dict[str, Any]:
    """
    Get summary of design analysis
    
    **Returns**: Summary of all frames analyzed in a file
    """
    try:
        # This would retrieve cached analysis in production
        # For demo, run fresh analysis
        analyses = await figma_review_service.review_design(file_key=file_key)
        
        # Build summary
        total_issues = sum(len(a.issues) for a in analyses)
        avg_score = sum(a.overall_score for a in analyses) / len(analyses) if analyses else 0
        
        critical_issues = sum(
            1 for a in analyses
            for issue in a.issues
            if issue.severity == "critical"
        )
        
        return {
            "file_key": file_key,
            "frames_analyzed": len(analyses),
            "average_score": round(avg_score, 1),
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "analyses": [
                {
                    "frame_name": a.frame_name,
                    "score": a.overall_score,
                    "issues_count": len(a.issues)
                }
                for a in analyses
            ]
        }
        
    except Exception as e:
        logger.error("Failed to get analysis", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis: {str(e)}"
        )
