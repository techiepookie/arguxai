/**
 * ArguxAI Settings Page
 */

router.register('/settings', function () {
    const view = document.getElementById('app-view');
    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Settings</h1>
                <p class="text-secondary">Configure platform integrations and engine preferences</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-primary">Save All Changes</button>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Compute & Intelligence</h2>
                </div>
                <div class="form-group">
                    <label class="form-label">DeepSeek API Key</label>
                    <input type="password" class="form-input" value="••••••••••••••••" />
                    <p class="text-muted mt-1" style="font-size: 0.75rem;">Used for AI diagnosis and funnel generation</p>
                </div>
                <div class="form-group">
                    <label class="form-label">Model Selection</label>
                    <select class="form-select">
                        <option>DeepSeek-V3 (Standard)</option>
                        <option>DeepSeek-R1 (Advanced Reasoning)</option>
                    </select>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Ecosystem Identifiers</h2>
                </div>
                <div class="form-group">
                    <label class="form-label">GitHub Installation ID</label>
                    <input type="text" class="form-input" placeholder="e.g., 582910" />
                </div>
                <div class="form-group">
                    <label class="form-label">Jira Host Domain</label>
                    <input type="text" class="form-input" placeholder="org-name.atlassian.net" />
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Real-time Notifications</h2>
                </div>
                <div class="form-group">
                    <label class="form-label">Slack Webhook URL</label>
                    <input type="password" class="form-input" placeholder="https://hooks.slack.com/..." />
                </div>
                <div class="form-group" style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid var(--border); padding-top: 1rem;">
                    <div>
                        <div style="font-weight: 600;">Critical Anomaly Alerts</div>
                        <div class="text-secondary" style="font-size: 0.8125rem;">Trigger Slack/Email on critical drops</div>
                    </div>
                    <div class="badge badge-high">Enabled</div>
                </div>
            </div>
        </div>
    `;
});

