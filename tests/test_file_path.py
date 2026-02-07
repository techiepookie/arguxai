#!/usr/bin/env python3
"""Test file path in GitHub"""

import asyncio
import httpx

async def test():
    token = "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"
    
    # Test both paths
    paths = [
        "login.js",
        "demo-login-app/login.js"
    ]
    
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        for path in paths:
            url = f"https://api.github.com/repos/techiepookie/demo-login-app/contents/{path}"
            r = await client.get(url)
            print(f"{path}: {r.status_code}")
            if r.status_code == 200:
                print(f"  ✅ Found!")
            else:
                print(f"  ❌ Not found")

asyncio.run(test())
