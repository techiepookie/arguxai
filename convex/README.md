# ArguxAI Convex Backend

This directory contains the Convex backend schema and functions for ArguxAI.

## Setup

1. **Install Convex CLI:**
   ```bash
   npm install -g convex
   ```

2. **Initialize Convex project:**
   ```bash
   npx convex dev
   ```
   
   This will:
   - Create a Convex project (if needed)
   - Generate the `_generated/` directory with TypeScript types
   - Start the development server
   - Watch for changes and auto-deploy

3. **Deploy to production:**
   ```bash
   npx convex deploy
   ```

4. **Update `.env` with Convex URL:**
   After running `convex dev`, copy the deployment URL and add to `.env`:
   ```
   CONVEX_URL=https://your-deployment.convex.cloud
   ```

## Schema

### `events` Table
Stores all user interaction events from the ArguxAI SDK.

**Indexes:**
- `by_timestamp` - For time-range queries
- `by_session` - For session analytics
- `by_funnel_step` - For funnel analysis
- `by_user` - For user tracking
- `by_funnel_and_time` - Compound index for efficient anomaly detection

### `issues` Table
Stores detected anomalies and their diagnostic information.

**Indexes:**
- `by_funnel_step` - Group issues by funnel step
- `by_status` - Filter by resolution status
- `by_detected_at` - Sort by detection time

## Functions

### Events (`events.ts`)
- `insertBatch` - Store multiple events atomically
- `queryByFunnelAndTime` - Get events for a funnel step in a time range
- `queryByTimeRange` - Get all events in a time range
- `list` - Get all events (debugging)
- `countByFunnelStep` - Count events for metrics

### Issues (`issues.ts`)
- `create` - Create a new issue
- `updateDiagnosis` - Add AI diagnosis to an issue  
- `updateJiraTicket` - Link Jira ticket to issue
- `updateGitHubPR` - Link GitHub PR to issue
- `getById` - Fetch issue by ID
- `list` - Get all issues

## Usage from Python

The Python client in `app/integrations/convex_client.py` calls these functions:

```python
# Insert events
await convex_client.mutation("events:insertBatch", {"events": events})

# Query events
events = await convex_client.query("events:queryByFunnelAndTime", {
    "funnel_step": "login_page",
    "start_time": start_ms,
    "end_time": end_ms
})
```
