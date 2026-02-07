#!/usr/bin/env python3
"""Test PR creation to see the exact error"""

import asyncio
import httpx

async def test():
    token = "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"
    repo = "techiepookie/demo-login-app"
    
    async with httpx.AsyncClient(
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    ) as client:
        
        # Try to create PR
        url = f"https://api.github.com/repos/{repo}/pulls"
        data = {
            "title": "Test PR",
            "body": "Test description",
            "head": "fix/login-button-click-20260207",
            "base": "main"
        }
        
        print(f"Creating PR with data: {data}")
        response = await client.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

asyncio.run(test())
