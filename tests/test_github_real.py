#!/usr/bin/env python3
"""Test real GitHub integration"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.github_client import github_client
from app.core.logging import logger


async def test_github():
    """Test GitHub API"""
    
    print("\n" + "="*60)
    print("Testing GitHub Integration")
    print("="*60 + "\n")
    
    # Test 1: Health check
    print("1. Testing GitHub API connection...")
    is_healthy = await github_client.health_check()
    
    if is_healthy:
        print("   ✅ GitHub API is accessible\n")
    else:
        print("   ❌ GitHub API is not accessible")
        print("   Check your GITHUB_TOKEN in .env\n")
        return False
    
    # Test 2: Check if file exists
    print("2. Checking if file exists in repository...")
    
    repository = "techiepookie/demo-login-app"
    file_path = "demo-login-app/login.js"
    
    try:
        content, sha = await github_client.get_file_content(
            repo=repository,
            file_path=file_path,
            branch="main"
        )
        
        print(f"   ✅ File found!")
        print(f"   Path: {file_path}")
        print(f"   Size: {len(content)} bytes")
        print(f"   SHA: {sha[:8]}...\n")
        
        return True
        
    except Exception as e:
        print(f"   ❌ File not found")
        print(f"   Error: {str(e)}\n")
        
        print("Trying alternative paths...")
        
        # Try other common paths
        alt_paths = [
            "login.js",
            "index.html",
            "README.md"
        ]
        
        for alt_path in alt_paths:
            try:
                content, sha = await github_client.get_file_content(
                    repo=repository,
                    file_path=alt_path,
                    branch="main"
                )
                print(f"   ✅ Found: {alt_path}")
                return True
            except:
                print(f"   ❌ Not found: {alt_path}")
        
        return False


if __name__ == "__main__":
    success = asyncio.run(test_github())
    sys.exit(0 if success else 1)
