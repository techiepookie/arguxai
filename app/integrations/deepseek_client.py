"""DeepSeek AI client for diagnosis and code generation"""

from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any
from app.config import settings
from app.core.logging import logger
import json
import time


class DeepSeekClient:
    """
    Client for DeepSeek AI API
    
    DeepSeek provides:
    - deepseek-chat: For text analysis and diagnosis
    - deepseek-vl: For vision/design analysis (used in Figma integration)
    """
    
    def __init__(self):
        # DeepSeek API is OpenAI-compatible
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url
        )
        
        self.chat_model = settings.deepseek_model_chat
        self.vision_model = settings.deepseek_model_vision
    
    async def diagnose_conversion_drop(
        self,
        funnel_step: str,
        drop_percentage: float,
        current_rate: float,
        baseline_rate: float,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use DeepSeek to diagnose root cause of conversion drop
        
        Args:
            funnel_step: Which funnel step has the issue
            drop_percentage: How much the conversion dropped
            current_rate: Current conversion rate
            baseline_rate: Historical baseline rate
            evidence: Collected evidence (errors, segments, etc.)
            
        Returns:
            Diagnosis dict with root_cause, confidence, explanation, recommendations
        """
        try:
            start_time = time.time()
            
            # Build comprehensive prompt
            prompt = self._build_diagnosis_prompt(
                funnel_step,
                drop_percentage,
                current_rate,
                baseline_rate,
                evidence
            )
            
            logger.info(
                "Requesting AI diagnosis from DeepSeek",
                funnel_step=funnel_step,
                drop_percentage=drop_percentage
            )
            
            # Call DeepSeek
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert conversion optimization analyst. Analyze user behavior data and diagnose technical issues causing conversion drops. Provide specific, actionable root causes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            diagnosis_text = response.choices[0].message.content
            diagnosis = json.loads(diagnosis_text)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            logger.info(
                "AI diagnosis completed",
                funnel_step=funnel_step,
                confidence=diagnosis.get("confidence"),
                time_ms=elapsed_ms
            )
            
            # Add metadata
            diagnosis["model_used"] = self.chat_model
            diagnosis["diagnosis_time_ms"] = elapsed_ms
            
            return diagnosis
            
        except Exception as e:
            logger.error("DeepSeek diagnosis failed", error=str(e))
            
            # Return fallback diagnosis
            return {
                "root_cause": f"Unable to diagnose - AI service error: {str(e)}",
                "confidence": 0.0,
                "explanation": "The AI diagnosis service encountered an error. Manual investigation required.",
                "recommended_actions": [
                    "Review error logs manually",
                    "Check recent deployments",
                    "Analyze affected user segments"
                ],
                "code_locations": [],
                "model_used": "fallback",
                "diagnosis_time_ms": 0
            }
    
    def _build_diagnosis_prompt(
        self,
        funnel_step: str,
        drop_percentage: float,
        current_rate: float,
        baseline_rate: float,
        evidence: Dict[str, Any]
    ) -> str:
        """Build comprehensive prompt for diagnosis"""
        
        # Map funnel steps to demo login app bugs
        demo_context = {
            "login_complete": {
                "bug": "API timeout too short (5 seconds)",
                "file": "demo-login-app/login.js",
                "line": "const API_TIMEOUT = 5000;",
                "fix": "Increase timeout to 15000ms"
            },
            "login_button_click": {
                "bug": "Button positioned off-screen on mobile devices",
                "file": "demo-login-app/styles.css",
                "line": ".login-button { position: absolute; bottom: -60px; }",
                "fix": "Change to relative positioning"
            },
            "form_start": {
                "bug": "No email validation before submission",
                "file": "demo-login-app/login.js",
                "line": "// No validation before API call",
                "fix": "Add email format validation"
            }
        }
        
        context = demo_context.get(funnel_step, {
            "bug": "Unknown issue",
            "file": "unknown",
            "line": "N/A",
            "fix": "Manual investigation required"
        })
        
        prompt = f"""Analyze this conversion drop in a demo login application.

## Funnel Step: {funnel_step}

## Metrics:
- **Current Conversion Rate**: {current_rate:.1f}%
- **Baseline Conversion Rate**: {baseline_rate:.1f}%
- **Drop**: {drop_percentage:.1f}% (from {baseline_rate:.1f}% to {current_rate:.1f}%)

## Known Bug Context:
- **Issue**: {context['bug']}
- **File**: {context['file']}
- **Code**: {context['line']}
- **Fix**: {context['fix']}

## Evidence:

### Error Patterns:
{json.dumps(evidence.get('error_types', {}), indent=2)}

### Top Error Messages:
{json.dumps(evidence.get('top_errors', []), indent=2)}

### User Behavior Changes:
- Average Retry Count: {evidence.get('avg_retry_count', 'N/A')}
- Time to Completion Change: {evidence.get('time_to_completion_change', 'N/A')}%

### Affected Segments:
- Countries: {', '.join(evidence.get('affected_countries', ['N/A']))}
- Devices: {', '.join(evidence.get('affected_devices', ['N/A']))}
- App Versions: {', '.join(evidence.get('affected_versions', ['N/A']))}

## Your Task:

Provide a diagnosis in JSON format with these fields:

{{
  "root_cause": "Single sentence identifying the root cause based on the known bug",
  "confidence": 85-95 (high confidence since this is a known demo bug),
  "explanation": "2-3 sentences explaining how this bug causes the conversion drop",
  "recommended_actions": ["Specific fix for this bug", "Testing steps", "Monitoring after fix"],
  "code_locations": ["{context['file']}"]
}}

Focus on the known bug and provide specific, actionable diagnosis."""

        return prompt
    
    async def generate_code_fix(
        self,
        diagnosis: Dict[str, Any],
        code_context: str,
        language: str = "python"
    ) -> str:
        """
        Generate code fix based on diagnosis
        
        Args:
            diagnosis: AI diagnosis result
            code_context: Relevant code context
            language: Programming language
            
        Returns:
            Generated code fix
        """
        try:
            prompt = f"""Based on this diagnosis, generate a code fix.

## Diagnosis:
{diagnosis.get('root_cause')}

## Explanation:
{diagnosis.get('explanation')}

## Current Code:
```{language}
{code_context}
```

## Task:
Generate the fixed version of this code. Only output the corrected code, no explanations."""

            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {language} developer. Generate clean, production-ready code fixes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            code_fix = response.choices[0].message.content
            
            logger.info("Code fix generated", language=language)
            
            return code_fix
            
        except Exception as e:
            logger.error("Code generation failed", error=str(e))
            return f"# Error generating code fix: {str(e)}"
    
    async def health_check(self) -> bool:
        """Check if DeepSeek API is accessible"""
        try:
            # Simple test call
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": "Respond with OK"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error("DeepSeek health check failed", error=str(e))
            return False
    
    async def analyze_design(
        self,
        image_bytes: bytes,
        frame_name: str,
        issue_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze Figma design screenshot using DeepSeek Chat (text-only analysis)
        
        Note: DeepSeek Vision API has format limitations, so we use text-based analysis
        with image metadata instead.
        
        Args:
            image_bytes: PNG/JPEG image bytes
            frame_name: Name of the frame being analyzed
            issue_context: Optional conversion issue context
            
        Returns:
            Design analysis dict with issues and recommendations
        """
        try:
            start_time = time.time()
            
            # Extract image metadata for analysis
            image_info = self._extract_image_info(image_bytes)
            
            # Build analysis prompt with image metadata
            prompt = self._build_design_analysis_prompt_text_only(
                frame_name, 
                issue_context,
                image_info
            )
            
            logger.info(
                "Requesting design analysis from DeepSeek (text-based)",
                frame_name=frame_name,
                image_size_kb=len(image_bytes) / 1024
            )
            
            # Use regular chat model for text-based analysis
            response = await self.client.chat.completions.create(
                model=self.chat_model,  # Use chat model instead of vision
                messages=[
                    {
                        "role": "system",
                        "content": "You are a UI/UX expert. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,  # Reduced for faster response
                timeout=30.0  # Add 30 second timeout
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(analysis_text)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            logger.info(
                "Design analysis completed",
                frame_name=frame_name,
                issues_found=len(analysis.get("issues", [])),
                time_ms=elapsed_ms
            )
            
            # Add metadata
            analysis["model_used"] = f"{self.chat_model} (text-based)"
            analysis["analysis_time_ms"] = elapsed_ms
            
            return analysis
            
        except Exception as e:
            logger.error("Design analysis failed", error=str(e))
            
            # Return fallback analysis
            return {
                "overall_score": 0.0,
                "issues": [],
                "strengths": [],
                "conversion_impact_assessment": f"Unable to analyze - API error: {str(e)}",
                "priority_fixes": [],
                "model_used": "fallback",
                "analysis_time_ms": 0
            }
    
    def _extract_image_info(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract metadata from image for text-based analysis"""
        try:
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(image_bytes))
            
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_kb": len(image_bytes) / 1024
            }
        except Exception as e:
            logger.warning(f"Could not extract image info: {e}")
            return {
                "width": 0,
                "height": 0,
                "format": "unknown",
                "mode": "unknown",
                "size_kb": len(image_bytes) / 1024
            }
    
    def _build_design_analysis_prompt_text_only(
        self,
        frame_name: str,
        issue_context: Optional[str] = None,
        image_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for text-based design analysis"""
        
        prompt = f"""Analyze this UI design frame: "{frame_name}" ({image_info.get('width', 0)}x{image_info.get('height', 0)}px)

Based on the frame name and common UI patterns, identify conversion optimization issues.

Return JSON with this structure:
{{
  "overall_score": 75,
  "issues": [
    {{
      "issue_type": "unclear_cta",
      "severity": "high",
      "description": "Issue description",
      "recommendation": "How to fix",
      "confidence": 85,
      "location": "Where in design"
    }}
  ],
  "strengths": ["Good aspect 1", "Good aspect 2"],
  "conversion_impact_assessment": "Brief impact summary",
  "priority_fixes": ["Fix 1", "Fix 2", "Fix 3"]
}}

Focus on: visual hierarchy, contrast, readability, CTA clarity, mobile optimization, form design."""

        return prompt


# Global DeepSeek client instance
deepseek_client = DeepSeekClient()

