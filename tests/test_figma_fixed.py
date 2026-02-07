#!/usr/bin/env python3
"""
Test Figma integration with fixes for:
1. Image compression (413 error fix)
2. Text-based analysis (400 error fix)
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.figma_review_service import figma_review_service
from app.core.logging import logger


async def test_figma_integration():
    """Test Figma integration with real file"""
    
    print("\n" + "="*60)
    print("Testing Figma Integration (Fixed)")
    print("="*60 + "\n")
    
    # Test file from user
    file_key = "kOtzR4Si2060lDrAJFP7hJ"
    
    print(f"📋 Testing file: {file_key}")
    print(f"🔧 Fixes applied:")
    print(f"   - Image compression to <1MB")
    print(f"   - Text-based analysis (no vision API)")
    print(f"   - Reduced scale from 2.0 to 1.0")
    print()
    
    try:
        # Run design review
        print("🚀 Starting design review...\n")
        
        analyses = await figma_review_service.review_design(
            file_key=file_key,
            frame_ids=None,  # Analyze first 3 frames
            issue_context="Analyzing for conversion optimization opportunities"
        )
        
        print(f"\n✅ Analysis complete!")
        print(f"   Frames analyzed: {len(analyses)}")
        print()
        
        # Display results
        for i, analysis in enumerate(analyses, 1):
            print(f"\n{'='*60}")
            print(f"Frame {i}: {analysis.frame_name}")
            print(f"{'='*60}")
            
            # Check if it's an error response
            if analysis.frame_id == "error":
                print(f"❌ ERROR: {analysis.frame_name}")
                print(f"\n{analysis.conversion_impact_assessment}")
                print(f"\n💡 Suggested Actions:")
                for j, fix in enumerate(analysis.priority_fixes, 1):
                    print(f"   {j}. {fix}")
                continue
            
            print(f"Overall Score: {analysis.overall_score:.1f}/100")
            print(f"Model Used: {analysis.model_used}")
            print(f"Analysis Time: {analysis.analysis_time_ms}ms")
            print()
            
            if analysis.issues:
                print(f"🔍 Issues Found ({len(analysis.issues)}):")
                for issue in analysis.issues[:3]:  # Show top 3
                    print(f"   [{issue.severity.upper()}] {issue.issue_type.value}")
                    print(f"   → {issue.description}")
                    print(f"   → Fix: {issue.recommendation}")
                    print()
            
            if analysis.strengths:
                print(f"✨ Strengths:")
                for strength in analysis.strengths[:3]:
                    print(f"   • {strength}")
                print()
            
            print(f"💡 Conversion Impact:")
            print(f"   {analysis.conversion_impact_assessment}")
            print()
            
            if analysis.priority_fixes:
                print(f"🎯 Priority Fixes:")
                for j, fix in enumerate(analysis.priority_fixes, 1):
                    print(f"   {j}. {fix}")
        
        print(f"\n{'='*60}")
        print("✅ All tests passed!")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_figma_integration())
    sys.exit(0 if success else 1)
