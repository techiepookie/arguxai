"""Figma API client for design review"""

import httpx
import base64
import asyncio
from typing import List, Dict, Any, Optional
from app.config import settings
from app.core.logging import logger
from app.models.figma import FigmaFrame, FigmaNodeType


class FigmaClient:
    """
    Figma REST API client
    
    Provides:
    - File metadata fetching
    - Frame/node listing  
    - Image rendering (screenshots)
    - Comment posting (annotations)
    - Rate limiting and retry logic
    """
    
    def __init__(self):
        self.access_token = settings.figma_access_token
        self.base_url = "https://api.figma.com/v1"
        
        # HTTP client with auth
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "X-Figma-Token": self.access_token
            }
        )
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
    
    async def _rate_limit(self):
        """Enforce rate limiting between requests"""
        import time
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def get_file_metadata(self, file_key: str) -> Dict[str, Any]:
        """
        Get file metadata and structure
        
        Args:
            file_key: Figma file key from URL
            
        Returns:
            File metadata dict
        """
        try:
            await self._rate_limit()
            
            url = f"{self.base_url}/files/{file_key}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(
                "Figma file metadata fetched",
                file_key=file_key,
                name=data.get("name")
            )
            
            return data
            
        except Exception as e:
            logger.error("Failed to fetch Figma file", error=str(e), file_key=file_key)
            raise
    
    async def get_frames(self, file_key: str) -> List[FigmaFrame]:
        """
        Get all top-level frames from a Figma file
        
        Args:
            file_key: Figma file key
            
        Returns:
            List of frames
        """
        try:
            metadata = await self.get_file_metadata(file_key)
            
            frames = []
            
            # Navigate document structure
            document = metadata.get("document", {})
            
            # Recursively find frames
            def extract_frames(node: Dict[str, Any]):
                node_type = node.get("type")
                
                # Check if it's a frame/screen
                if node_type in ["FRAME", "COMPONENT"]:
                    # Get bounds
                    absolute_bounds = node.get("absoluteBoundingBox", {})
                    
                    frame = FigmaFrame(
                        id=node.get("id"),
                        name=node.get("name"),
                        node_type=FigmaNodeType(node_type),
                        width=absolute_bounds.get("width", 0),
                        height=absolute_bounds.get("height", 0)
                    )
                    frames.append(frame)
                
                # Recurse into children
                for child in node.get("children", []):
                    extract_frames(child)
            
            extract_frames(document)
            
            logger.info(
                "Frames extracted from Figma file",
                file_key=file_key,
                frame_count=len(frames)
            )
            
            return frames
            
        except Exception as e:
            logger.error("Failed to extract frames", error=str(e))
            raise
    
    async def render_frame_image(
        self,
        file_key: str,
        node_id: str,
        scale: float = 1.0,  # Reduced from 2.0 to save size
        max_size_kb: int = 1024  # Max 1MB for API
    ) -> bytes:
        """
        Render a frame as PNG image, compressed to fit API limits
        
        Args:
            file_key: Figma file key
            node_id: Frame node ID
            scale: Image scale (1.0 = normal, 2.0 = 2x retina)
            max_size_kb: Maximum size in KB (default 1MB)
            
        Returns:
            PNG image bytes (compressed if needed)
        """
        try:
            await self._rate_limit()
            
            # Get image URL from Figma
            url = f"{self.base_url}/images/{file_key}"
            params = {
                "ids": node_id,
                "format": "png",
                "scale": scale
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            image_url = data.get("images", {}).get(node_id)
            
            if not image_url:
                raise ValueError(f"No image URL returned for node {node_id}")
            
            # Download the image
            image_response = await self.client.get(image_url)
            image_response.raise_for_status()
            
            image_bytes = image_response.content
            original_size_kb = len(image_bytes) / 1024
            
            # Compress if too large
            if original_size_kb > max_size_kb:
                logger.info(
                    "Image too large, compressing",
                    original_kb=original_size_kb,
                    max_kb=max_size_kb
                )
                image_bytes = await self._compress_image(image_bytes, max_size_kb)
            
            final_size_kb = len(image_bytes) / 1024
            
            logger.info(
                "Frame image rendered",
                file_key=file_key,
                node_id=node_id,
                original_kb=original_size_kb,
                final_kb=final_size_kb
            )
            
            return image_bytes
            
        except Exception as e:
            logger.error(
                "Failed to render frame image",
                error=str(e),
                file_key=file_key,
                node_id=node_id
            )
            raise
    
    async def _compress_image(self, image_bytes: bytes, max_size_kb: int) -> bytes:
        """
        Compress image to fit within size limit
        
        Args:
            image_bytes: Original image bytes
            max_size_kb: Maximum size in KB
            
        Returns:
            Compressed image bytes
        """
        try:
            from PIL import Image
            import io
            
            # Load image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed (remove alpha channel)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Try different quality levels
            for quality in [85, 75, 65, 55, 45]:
                output = io.BytesIO()
                
                # Resize if still too large
                if quality < 60:
                    # Reduce dimensions by 25%
                    new_size = (int(img.width * 0.75), int(img.height * 0.75))
                    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    img_resized.save(output, format='JPEG', quality=quality, optimize=True)
                else:
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                
                compressed_bytes = output.getvalue()
                size_kb = len(compressed_bytes) / 1024
                
                if size_kb <= max_size_kb:
                    logger.info(
                        "Image compressed successfully",
                        quality=quality,
                        size_kb=size_kb
                    )
                    return compressed_bytes
            
            # If still too large, return best effort
            logger.warning(
                "Could not compress image below limit",
                final_kb=size_kb,
                max_kb=max_size_kb
            )
            return compressed_bytes
            
        except Exception as e:
            logger.error("Image compression failed", error=str(e))
            # Return original if compression fails
            return image_bytes
    
    async def post_comment(
        self,
        file_key: str,
        message: str,
        node_id: Optional[str] = None,
        x: Optional[float] = None,
        y: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Post a comment/annotation to Figma file
        
        Args:
            file_key: Figma file key
            message: Comment text
            node_id: Optional node to attach comment to
            x, y: Optional coordinates (0-1 normalized)
            
        Returns:
            Comment data
        """
        try:
            url = f"{self.base_url}/files/{file_key}/comments"
            
            # Build comment payload
            payload: Dict[str, Any] = {
                "message": message
            }
            
            # Add position if provided
            if node_id and x is not None and y is not None:
                payload["client_meta"] = {
                    "node_id": node_id,
                    "node_offset": {
                        "x": x,
                        "y": y
                    }
                }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            comment_data = response.json()
            
            logger.info(
                "Comment posted to Figma",
                file_key=file_key,
                comment_id=comment_data.get("id")
            )
            
            return comment_data
            
        except Exception as e:
            logger.error("Failed to post comment", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check if Figma API is accessible"""
        try:
            if not self.access_token:
                return False
            
            # Simple API call to verify token
            url = f"{self.base_url}/me"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error("Figma health check failed", error=str(e))
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global Figma client instance
figma_client = FigmaClient()
