#!/usr/bin/env python3
"""Test GitHub write access with new token"""

import asyncio
import sys
import os
import httpx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.core.logging import logger


async def test_github_write():
    """Test GitHub write access"""
    
    print("\n" + "="*60)
    print("Testing GitHub Write Access")
    print("="*60 + "\n")
    
    token = settings.github_token
    repo = "techiepookie/demo-login-app"
    
    if not token:
        print("❌ No GitHub token configured\n")
        return False
    
    print(f"Token: {token[:10]}...{token[-4:]}")
    print(f"Repository: {repo}\n")
    
    async with httpx.AsyncClient(
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        timeout=30.0
    ) as client:
        
        # Test 1: Check user
        print("1. Checking authenticated user...")
        try:
            response = await client.get("https://api.github.com/user")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ Authenticated as: {user_data.get('login')}\n")
            else:
                print(f"   ❌ Auth failed: {response.status_code}\n")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            return False
        
        # Test 2: Check repository exists
        print("2. Checking repository access...")
        try:
            response = await client.get(f"https://api.github.com/repos/{repo}")
            if response.status_code == 200:
                repo_data = response.json()
                print(f"   ✅ Repository found: {repo_data.get('full_name')}")
                print(f"   Owner: {repo_data.get('owner', {}).get('login')}")
                print(f"   Private: {repo_data.get('private')}")
                print(f"   Permissions: {repo_data.get('permissions')}\n")
            elif response.status_code == 404:
                print(f"   ❌ Repository not found or no access")
                print(f"   Status: {response.status_code}\n")
                return False
            else:
                print(f"   ❌ Error: {response.status_code}\n")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            return False
        
        # Test 3: Check refs access
        print("3. Checking refs/branches access...")
        try:
            response = await client.get(f"https://api.github.com/repos/{repo}/git/refs")
            if response.status_code == 200:
                refs = response.json()
                print(f"   ✅ Can access refs ({len(refs)} refs found)")
                print(f"   Sample refs: {[r.get('ref') for r in refs[:3]]}\n")
                return True
            else:
                print(f"   ❌ Cannot access refs")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}\n")
                
                # Check if it's a permissions issue
                if response.status_code == 404:
                    print("   This usually means:")
                    print("   - Token doesn't have 'repo' scope")
                    print("   - Repository doesn't exist")
                    print("   - You don't have write access to this repo\n")
                
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_github_write())
    sys.exit(0 if success else 1)
