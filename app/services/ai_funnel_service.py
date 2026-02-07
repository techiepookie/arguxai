"""
AI-powered funnel generation service
Uses DeepSeek for intelligent funnel creation and prompt enhancement
"""

import httpx
import json
from typing import List
from app.config import settings
from app.models.funnels import (
    FunnelCreate, FunnelStep,
    AIPromptEnhanceResponse, AIFunnelGenerateResponse
)
from app.core.logging import logger


class AIFunnelService:
    """AI service for funnel generation using DeepSeek"""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = "https://api.deepseek.com/v1"
    
    async def enhance_prompt(self, user_prompt: str) -> AIPromptEnhanceResponse:
        """
        Enhance user's funnel prompt with best practices and clarity
        
        Args:
            user_prompt: User's original prompt
            
        Returns:
            Enhanced prompt with improvements list
        """
        system_prompt = """You are a conversion funnel expert. Your job is to take a user's vague or incomplete funnel idea and enhance it into a detailed, actionable prompt.

Best practices to apply:
- Add specific event types (page_view, button_click, form_submit, etc.)
- Clarify ambiguous steps
- Include typical user flow details
- Suggest relevant tracking points
- Add business context where missing

Return JSON with:
{
  "enhanced_prompt": "detailed enhanced prompt",
  "improvements": ["what you improved 1", "what you improved 2", ...]
}"""

        user_message = f"""Original prompt: "{user_prompt}"

Enhance this prompt for funnel generation."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": 0.7,
                        "response_format": {"type": "json_object"}
                    }
                )
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                data = json.loads(content)
                
                logger.info("Prompt enhanced", original_length=len(user_prompt), enhanced_length=len(data["enhanced_prompt"]))
                
                return AIPromptEnhanceResponse(
                    original_prompt=user_prompt,
                    enhanced_prompt=data["enhanced_prompt"],
                    improvements=data.get("improvements", [])
                )
                
        except Exception as e:
            logger.error("Failed to enhance prompt", error=str(e))
            # Fallback: return original with basic improvements
            return AIPromptEnhanceResponse(
                original_prompt=user_prompt,
                enhanced_prompt=user_prompt + " (Track all key user actions and conversion points)",
                improvements=["Added reminder to track key actions"]
            )
    
    async def generate_funnel(self, prompt: str, available_events: List[str] = None) -> AIFunnelGenerateResponse:
        """
        Generate complete funnel structure from prompt
        
        Args:
            prompt: Detailed prompt describing desired funnel
            available_events: Optional list of actual event types in the system
            
        Returns:
            Generated funnel with reasoning
        """
        events_context = ""
        if available_events:
            events_context = f"\n\nAvailable Event Types in System (PREFER THESE):\n- " + "\n- ".join(available_events[:20])

        system_prompt = f"""You are a conversion funnel architect. Generate a complete funnel structure from the user's description.{events_context}

A funnel should have:
- Clear name and description
- 3-7 sequential steps
- Each step has: name, event_type, order
- Event types: page_view, button_click, form_submit, custom (OR one from the available list)

Return JSON:
{{
  "funnel": {{
    "name": "Funnel Name",
    "description": "What this funnel tracks",
    "steps": [
      {{"name": "Step 1", "event_type": "page_view", "order": 1}},
      {{"name": "Step 2", "event_type": "button_click", "order": 2}},
      ...
    ],
    "created_by_ai": true
  }},
  "reasoning": "Why I structured it this way"
}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Generate funnel: {prompt}"}
                        ],
                        "temperature": 0.8,
                        "response_format": {"type": "json_object"}
                    }
                )
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                data = json.loads(content)
                
                # Convert to FunnelCreate model
                funnel_data = data["funnel"]
                steps = [
                    FunnelStep(
                        name=step["name"],
                        event_type=step["event_type"],
                        order=step["order"]
                    )
                    for step in funnel_data["steps"]
                ]
                
                funnel = FunnelCreate(
                    name=funnel_data["name"],
                    description=funnel_data.get("description"),
                    steps=steps,
                    created_by_ai=True,
                    ai_prompt=prompt
                )
                
                logger.info("Funnel generated by AI", name=funnel.name, steps_count=len(steps))
                
                return AIFunnelGenerateResponse(
                    funnel=funnel,
                    reasoning=data.get("reasoning", "AI-generated funnel structure")
                )
                
        except Exception as e:
            logger.error("Failed to generate funnel", error=str(e))
            # Fallback: generate basic funnel
            return self._generate_fallback_funnel(prompt)
    
    def _generate_fallback_funnel(self, prompt: str) -> AIFunnelGenerateResponse:
        """Generate basic fallback funnel if AI fails"""
        funnel = FunnelCreate(
            name="Basic Funnel",
            description=f"Auto-generated from: {prompt[:100]}",
            steps=[
                FunnelStep(name="Start", event_type="page_view", order=1),
                FunnelStep(name="Action", event_type="button_click", order=2),
                FunnelStep(name="Complete", event_type="custom", order=3)
            ],
            created_by_ai=True,
            ai_prompt=prompt
        )
        
        return AIFunnelGenerateResponse(
            funnel=funnel,
            reasoning="Fallback basic funnel (AI service unavailable)"
        )


# Global instance
ai_funnel_service = AIFunnelService()
