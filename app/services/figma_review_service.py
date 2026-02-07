"""Figma design review service"""

from typing import List, Dict, Any, Optional
import time
from app.models.figma import (
    FigmaFrame, DesignAnalysis, DesignIssue, DesignIssueType
)
from app.integrations.figma_client import figma_client
from app.integrations.deepseek_client import deepseek_client
from app.core.logging import logger
from app.config import settings


class FigmaReviewService:
    """
    Orchestrate Figma design review workflow
    
    Workflow:
    1. Fetch file and frames from Figma
    2. Render frame screenshots
    3. Analyze with DeepSeek Vision
    4. Post annotations back to Figma
    5. Return comprehensive analysis
    """
    
    async def review_design(
        self,
        file_key: str,
        frame_ids: Optional[List[str]] = None,
        issue_context: Optional[str] = None
    ) -> List[DesignAnalysis]:
        """
        Review Figma design for conversion issues
        
        Args:
            file_key: Figma file key
            frame_ids: Specific frames to analyze (all if None)
            issue_context: Optional context about conversion issue
            
        Returns:
            List of design analyses
        """
        try:
            logger.info(
                "Starting Figma design review",
                file_key=file_key,
                frame_count=len(frame_ids) if frame_ids else "all"
            )
            
            # Check if Figma token is configured
            if not settings.figma_access_token:
                logger.warning("Figma access token not configured")
                return [{
                    "frame_id": "error",
                    "frame_name": "Configuration Error",
                    "overall_score": 0,
                    "issues": [],
                    "strengths": [],
                    "conversion_impact_assessment": "Figma access token is not configured. Please add FIGMA_ACCESS_TOKEN to your .env file.",
                    "priority_fixes": ["Add Figma token to .env", "Restart the server", "Try analysis again"],
                    "model_used": "error",
                    "analysis_time_ms": 0
                }]
            
            # Step 1: Get frames from file
            try:
                all_frames = await figma_client.get_frames(file_key)
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    return [{
                        "frame_id": "error",
                        "frame_name": "Rate Limit Exceeded",
                        "overall_score": 0,
                        "issues": [],
                        "strengths": [],
                        "conversion_impact_assessment": "Figma API rate limit exceeded (429 error). Please wait 2-3 minutes before trying again. This is a temporary limit from Figma's API.",
                        "priority_fixes": ["Wait 2-3 minutes", "Try again", "Rate limits reset automatically"],
                        "model_used": "error",
                        "analysis_time_ms": 0
                    }]
                elif "404" in error_msg or "403" in error_msg:
                    return [{
                        "frame_id": "error",
                        "frame_name": "File Access Error",
                        "overall_score": 0,
                        "issues": [],
                        "strengths": [],
                        "conversion_impact_assessment": "Cannot access Figma file. The file may be private or your token doesn't have permission. Verify the file URL and token permissions.",
                        "priority_fixes": ["Check file is not private", "Verify token has file access", "Try a different file"],
                        "model_used": "error",
                        "analysis_time_ms": 0
                    }]
                else:
                    logger.error(f"Failed to fetch Figma frames: {str(e)}")
                    return [{
                        "frame_id": "error",
                        "frame_name": "API Error",
                        "overall_score": 0,
                        "issues": [],
                        "strengths": [],
                        "conversion_impact_assessment": f"Failed to fetch Figma file: {error_msg}",
                        "priority_fixes": ["Check file URL", "Verify token", "Check network connection"],
                        "model_used": "error",
                        "analysis_time_ms": 0
                    }]
            
            # Filter to specific frames if requested
            if frame_ids:
                frames = [f for f in all_frames if f.id in frame_ids]
            else:
                # Analyze top 3 frames by default
                frames = all_frames[:3]
            
            if not frames:
                logger.warning("No frames found in Figma file")
                return [{
                    "frame_id": "error",
                    "frame_name": "No Frames Found",
                    "overall_score": 0,
                    "issues": [],
                    "strengths": [],
                    "conversion_impact_assessment": "No frames found in the Figma file. The file may be empty or contain only components/pages without frames.",
                    "priority_fixes": ["Check file has frames", "Try a different file", "Ensure frames are top-level"],
                    "model_used": "error",
                    "analysis_time_ms": 0
                }]
            
            logger.info(f"Analyzing {len(frames)} frames")
            
            # Step 2-3: Analyze each frame
            analyses = []
            
            for frame in frames:
                try:
                    # Render screenshot
                    image_bytes = await figma_client.render_frame_image(
                        file_key=file_key,
                        node_id=frame.id
                    )
                    
                    # Analyze with DeepSeek Vision
                    analysis_dict = await deepseek_client.analyze_design(
                        image_bytes=image_bytes,
                        frame_name=frame.name,
                        issue_context=issue_context
                    )
                    
                    # Convert to DesignAnalysis model
                    issues = [
                        DesignIssue(**issue_data)
                        for issue_data in analysis_dict.get("issues", [])
                    ]
                    
                    analysis = DesignAnalysis(
                        frame_id=frame.id,
                        frame_name=frame.name,
                        overall_score=analysis_dict.get("overall_score", 0),
                        issues=issues,
                        strengths=analysis_dict.get("strengths", []),
                        conversion_impact_assessment=analysis_dict.get("conversion_impact_assessment", ""),
                        priority_fixes=analysis_dict.get("priority_fixes", []),
                        model_used=analysis_dict.get("model_used", ""),
                        analysis_time_ms=analysis_dict.get("analysis_time_ms", 0)
                    )
                    
                    analyses.append(analysis)
                    
                    logger.info(
                        "Frame analyzed",
                        frame_name=frame.name,
                        score=analysis.overall_score,
                        issues=len(analysis.issues)
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to analyze frame {frame.name}: {str(e)}")
                    # Continue with other frames
                    continue
            
            # If no frames were successfully analyzed, return error
            if not analyses:
                logger.warning("No frames successfully analyzed")
                return [{
                    "frame_id": "error",
                    "frame_name": "Analysis Failed",
                    "overall_score": 0,
                    "issues": [],
                    "strengths": [],
                    "conversion_impact_assessment": "Unable to fetch Figma file. This may be due to: 1) API rate limits (429 error) - please wait a few minutes and try again, 2) File access permissions - ensure your Figma token has access to this file, 3) Network issues - check your connection.",
                    "priority_fixes": ["Wait a few minutes if rate limited", "Verify Figma token permissions", "Check file URL is correct"],
                    "model_used": "error",
                    "analysis_time_ms": 0
                }]
            
            return analyses
            
        except Exception as e:
            logger.error("Figma design review failed", error=str(e))
            # Return error message instead of demo
            return [{
                "frame_id": "error",
                "frame_name": "Analysis Failed",
                "overall_score": 0,
                "issues": [],
                "strengths": [],
                "conversion_impact_assessment": f"Unable to analyze Figma file: {str(e)}. Please check your Figma access token and file permissions.",
                "priority_fixes": ["Verify Figma token is valid", "Check file access permissions", "Ensure file URL is correct"],
                "model_used": "error",
                "analysis_time_ms": 0
            }]
    
    async def post_analysis_as_comments(
        self,
        file_key: str,
        analyses: List[DesignAnalysis]
    ) -> int:
        """
        Post design analysis as Figma comments
        
        Args:
            file_key: Figma file key
            analyses: Design analyses to post
            
        Returns:
            Number of comments posted
        """
        try:
            comments_posted = 0
            
            for analysis in analyses:
                # Build comment message
                message = self._format_analysis_comment(analysis)
                
                # Post to Figma
                await figma_client.post_comment(
                    file_key=file_key,
                    message=message,
                    node_id=analysis.frame_id
                )
                
                comments_posted += 1
            
            logger.info(
                "Analysis comments posted",
                file_key=file_key,
                count=comments_posted
            )
            
            return comments_posted
            
        except Exception as e:
            logger.error("Failed to post comments", error=str(e))
            raise
    
    def _format_analysis_comment(self, analysis: DesignAnalysis) -> str:
        """Format analysis as Figma comment"""
        
        message = f"""🤖 **ArguxAI Design Review**

**Overall Score**: {analysis.overall_score:.0f}/100

**Conversion Impact**:
{analysis.conversion_impact_assessment}

**Priority Fixes**:
"""
        
        for i, fix in enumerate(analysis.priority_fixes[:3], 1):
            message += f"{i}. {fix}\n"
        
        if analysis.issues:
            message += f"\n**Issues Found** ({len(analysis.issues)}):\n"
            
            for issue in analysis.issues[:5]:  # Top 5 issues
                severity_emoji = {
                    "critical": "🚨",
                    "high": "⚠️",
                    "medium": "⚡",
                    "low": "ℹ️"
                }.get(issue.severity, "•")
                
                message += f"\n{severity_emoji} **{issue.issue_type.value.replace('_', ' ').title()}** ({issue.severity})\n"
                message += f"  - {issue.description}\n"
                message += f"  - Fix: {issue.recommendation}\n"
        
        if analysis.strengths:
            message += f"\n✅ **Strengths**:\n"
            for strength in analysis.strengths[:3]:
                message += f"- {strength}\n"
        
        message += f"\n*Analyzed by {analysis.model_used} in {analysis.analysis_time_ms}ms*"
        
        return message


# Global service instance
figma_review_service = FigmaReviewService()
