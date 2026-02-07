#!/usr/bin/env python3
"""Check for existing PRs"""

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
        
        # List PRs
        url = f"https://api.github.com/repos/{repo}/pulls"
        response = await client.get(url)
        prs = response.json()
        
        print(f"Found {len(prs)} open PRs:")
        for pr in prs:
            print(f"  - #{pr['number']}: {pr['title']}")
            print(f"    Branch: {pr['head']['ref']}")
            print(f"    URL: {pr['html_url']}")
            print()

asyncio.run(test())
