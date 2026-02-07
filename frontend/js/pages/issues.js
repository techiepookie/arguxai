/**
 * Issues Page - Fully Functional
 */

router.register('/issues', async function () {
    await loadIssuesPage();
});

// Make loadIssueDetail globally accessible for dynamic routing
window.loadIssueDetail = loadIssueDetail;

async function loadIssuesPage() {
    const view = document.getElementById('app-view');

    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Issues Board</h1>
                <p class="text-secondary">Detected conversion anomalies and AI-diagnosed action items</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-outline" onclick="detectNewIssues()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    Scan for Anomalies
                </button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">All Open Issues</h2>
            </div>
            <div class="issues-list" id="issues-board-list">
                <div class="text-center p-3">Loading issues...</div>
            </div>
        </div>
    `;

    await loadIssuesList();
}

async function loadIssuesList() {
    const container = document.getElementById('issues-board-list');
    try {
        const issues = await api.listIssues();
        
        console.log('Issues loaded:', issues);
        
        if (!issues || issues.length === 0) {
            container.innerHTML = `
                <div class="text-center p-5">
                    <p class="text-muted">No issues found. Click "Scan for Anomalies" to detect conversion issues.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = issues.map(issue => {
            // Handle both anomaly object and direct properties
            const funnelStep = issue.funnel_step || (issue.anomaly && issue.anomaly.funnel_step) || 'Unknown';
            const dropPercentage = issue.drop_percentage || (issue.anomaly && issue.anomaly.drop_percentage) || 0;
            const currentRate = issue.current_conversion_rate || (issue.anomaly && issue.anomaly.current_conversion_rate) || 0;
            const baselineRate = issue.baseline_conversion_rate || (issue.anomaly && issue.anomaly.baseline_conversion_rate) || 0;
            const detectedAt = issue.detected_at || (issue.anomaly && issue.anomaly.detected_at) || Date.now();
            
            return `
                <div class="issue-item" onclick="window.location.hash='#/issues/${issue.id}'" style="cursor: pointer;">
                    <div class="issue-main">
                        <div class="issue-meta">
                            <span class="issue-id">ISS-${issue.id.slice(0, 6).toUpperCase()}</span>
                            <span class="badge badge-${issue.severity.toLowerCase()}">${issue.severity}</span>
                            <span class="badge" style="background: rgba(255,255,255,0.05); color: var(--text-secondary)">${issue.status}</span>
                        </div>
                        <div class="issue-title" style="font-size: 1.125rem; margin-top: 0.5rem;">${escapeHTML(funnelStep)} - Conversion Drop</div>
                        <div class="issue-details" style="font-size: 0.875rem; margin-top: 0.25rem;">
                            Conversion dropped by <span class="trend negative">${Math.round(dropPercentage)}%</span> 
                            (${baselineRate.toFixed(1)}% → ${currentRate.toFixed(1)}%)
                            · Detected ${formatTimeSince(detectedAt)}
                        </div>
                    </div>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--text-muted)">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Failed to load issues:', error);
        container.innerHTML = `
            <div class="text-center p-3">
                <p class="text-danger">Failed to load issues: ${error.message}</p>
                <button class="btn btn-primary" onclick="detectNewIssues()" style="margin-top: 1rem;">
                    Scan for Anomalies
                </button>
            </div>
        `;
    }
}

async function loadIssueDetail(issueId) {
    const view = document.getElementById('app-view');
    
    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Issue Details</h1>
                <p class="text-secondary">ISS-${issueId.slice(0, 6).toUpperCase()}</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-outline" onclick="window.location.hash='#/issues'">Back to List</button>
            </div>
        </div>
        <div id="issue-detail-content">Loading...</div>
    `;
    
    try {
        const issue = await api.getIssue(issueId);
        const detailContainer = document.getElementById('issue-detail-content');
        
        // Handle both anomaly object and direct properties
        const funnelStep = issue.funnel_step || (issue.anomaly && issue.anomaly.funnel_step) || 'Unknown';
        const dropPercentage = issue.drop_percentage || (issue.anomaly && issue.anomaly.drop_percentage) || 0;
        const currentRate = issue.current_conversion_rate || (issue.anomaly && issue.anomaly.current_conversion_rate) || 0;
        const baselineRate = issue.baseline_conversion_rate || (issue.anomaly && issue.anomaly.baseline_conversion_rate) || 0;
        const sigmaValue = issue.sigma_value || (issue.anomaly && issue.anomaly.sigma_value) || 0;
        const diagnosis = issue.diagnosis ? (typeof issue.diagnosis === 'string' ? issue.diagnosis : issue.diagnosis.root_cause) : null;
        
        detailContainer.innerHTML = `
            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Anomaly Overview</h2>
                        <span class="badge badge-${issue.severity.toLowerCase()}">${issue.severity}</span>
                    </div>
                    <div style="padding: 1rem 0;">
                        <div style="margin-bottom: 1.5rem;">
                            <div class="label">Funnel Step</div>
                            <div class="value" style="font-size: 1.5rem;">${escapeHTML(funnelStep)}</div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;">
                            <div>
                                <div class="label">Current Rate</div>
                                <div class="value trend negative">${currentRate.toFixed(1)}%</div>
                            </div>
                            <div>
                                <div class="label">Baseline Rate</div>
                                <div class="value">${baselineRate.toFixed(1)}%</div>
                            </div>
                            <div>
                                <div class="label">Drop Percentage</div>
                                <div class="value trend negative">${Math.round(dropPercentage)}%</div>
                            </div>
                            <div>
                                <div class="label">Statistical Significance</div>
                                <div class="value">${sigmaValue.toFixed(1)}σ</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">AI Diagnosis</h2>
                    </div>
                    ${diagnosis ? `
                        <div style="padding: 1rem; background: rgba(6, 182, 212, 0.05); border: 1px solid var(--primary-glow); border-radius: 8px;">
                            <p style="color: var(--text-primary); line-height: 1.6;">${escapeHTML(diagnosis)}</p>
                        </div>
                    ` : `
                        <button class="btn btn-primary" onclick="diagnoseIssue('${issue.id}')" style="width: 100%;">
                            🤖 Run AI Diagnosis
                        </button>
                    `}
                    
                    <div class="header-actions" style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border);">
                        <button class="btn btn-primary" onclick="generatePR('${issue.id}')">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                            </svg>
                            Generate GitHub PR
                        </button>
                        <button class="btn btn-outline" onclick="createJiraTicket('${issue.id}')">
                            Create Jira Ticket
                        </button>
                    </div>
                    
                    ${issue.fix_pr_url ? `
                        <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.75rem; color: var(--success); font-weight: 600; margin-bottom: 0.25rem;">✓ PR CREATED</div>
                            <a href="${issue.fix_pr_url}" target="_blank" style="color: var(--primary); font-size: 0.875rem;">${issue.fix_pr_url}</a>
                            <button class="btn btn-outline" onclick="loadPRDetailsInIssue('${issue.id}', '${issue.fix_pr_url}')" style="margin-top: 0.5rem; width: 100%; font-size: 0.875rem;">
                                View PR Details
                            </button>
                        </div>
                    ` : ''}
                    
                    ${issue.jira_ticket_key ? `
                        <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.75rem; color: var(--success); font-weight: 600; margin-bottom: 0.25rem;">✓ JIRA TICKET</div>
                            <div style="color: var(--text-primary); font-size: 0.875rem;">${issue.jira_ticket_key}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load issue detail:', error);
        document.getElementById('issue-detail-content').innerHTML = `
            <div class="card">
                <div class="text-center p-3 text-danger">Failed to load issue details: ${error.message}</div>
            </div>
        `;
    }
}

async function detectNewIssues() {
    try {
        showLoading();
        await api.detectIssues();
        hideLoading();
        showToast('Scan complete!', 'success');
        await loadIssuesList();
    } catch (error) {
        hideLoading();
        showToast('Scan failed: ' + error.message, 'error');
    }
}

async function diagnoseIssue(issueId) {
    try {
        showLoading();
        await api.diagnoseIssue(issueId);
        hideLoading();
        showToast('Diagnosis complete!', 'success');
        await loadIssueDetail(issueId);
    } catch (error) {
        hideLoading();
        showToast('Diagnosis failed: ' + error.message, 'error');
    }
}

async function generatePR(issueId) {
    try {
        showLoading();
        await api.generatePR(issueId);
        hideLoading();
        showToast('PR created successfully!', 'success');
        await loadIssueDetail(issueId);
    } catch (error) {
        hideLoading();
        showToast('PR generation failed: ' + error.message, 'error');
    }
}

async function createJiraTicket(issueId) {
    try {
        showLoading();
        await api.createJiraTicket(issueId);
        hideLoading();
        showToast('Jira ticket created!', 'success');
        await loadIssueDetail(issueId);
    } catch (error) {
        hideLoading();
        showToast('Ticket creation failed: ' + error.message, 'error');
    }
}



async function loadPRDetailsInIssue(issueId, prUrl) {
    try {
        showLoading();
        
        // Extract PR number from URL
        const prNumber = prUrl.split('/').pop();
        const repository = 'techiepookie/demo-login-app';
        
        // Fetch PR details
        const pr = await api.request(`/api/github/prs/${prNumber}?repository=${encodeURIComponent(repository)}`);
        
        hideLoading();
        
        // Find the issue detail content area and append PR details
        const detailContainer = document.getElementById('issue-detail-content');
        
        // Add PR details section
        const prDetailsHTML = `
            <div class="card" style="margin-top: 1.5rem;">
                <div class="card-header">
                    <h2 class="card-title">Pull Request Details</h2>
                    <a href="${pr.url}" target="_blank" class="btn btn-outline" style="font-size: 0.875rem;">
                        View on GitHub →
                    </a>
                </div>
                
                <div style="padding: 1rem 0;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span class="badge" style="background: rgba(6, 182, 212, 0.1); color: var(--primary);">PR #${pr.number}</span>
                        <span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">${pr.state}</span>
                    </div>
                    
                    <h4 style="margin-bottom: 0.5rem;">${escapeHTML(pr.title)}</h4>
                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1.5rem;">
                        ${escapeHTML(pr.user.login)} wants to merge ${pr.commits} commit${pr.commits !== 1 ? 's' : ''} into <code style="background: rgba(255,255,255,0.1); padding: 0.125rem 0.5rem; border-radius: 4px;">${pr.base_branch}</code> from <code style="background: rgba(255,255,255,0.1); padding: 0.125rem 0.5rem; border-radius: 4px;">${pr.branch}</code>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                        <div style="padding: 1rem; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Additions</div>
                            <div style="font-size: 1.5rem; color: var(--success); font-weight: 600;">+${pr.additions}</div>
                        </div>
                        <div style="padding: 1rem; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Deletions</div>
                            <div style="font-size: 1.5rem; color: #ef4444; font-weight: 600;">-${pr.deletions}</div>
                        </div>
                        <div style="padding: 1rem; background: rgba(6, 182, 212, 0.05); border: 1px solid var(--primary-glow); border-radius: 8px;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Files Changed</div>
                            <div style="font-size: 1.5rem; color: var(--primary); font-weight: 600;">${pr.changed_files}</div>
                        </div>
                    </div>
                    
                    ${pr.body ? `
                        <div style="margin-bottom: 1.5rem;">
                            <h4 style="margin-bottom: 0.5rem; font-size: 1rem;">Description</h4>
                            <div style="padding: 1rem; background: rgba(6, 182, 212, 0.05); border: 1px solid var(--primary-glow); border-radius: 8px; white-space: pre-wrap; font-size: 0.875rem; line-height: 1.6; max-height: 300px; overflow-y: auto;">
${escapeHTML(pr.body)}</div>
                        </div>
                    ` : ''}
                    
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="margin-bottom: 0.5rem; font-size: 1rem;">Commits (${pr.commits})</h4>
                        <div style="max-height: 200px; overflow-y: auto;">
                            ${pr.commit_messages.map(commit => `
                                <div style="padding: 0.75rem; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 0.5rem;">
                                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                                        <code style="background: rgba(6, 182, 212, 0.1); padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">${commit.sha}</code>
                                        <span style="font-size: 0.75rem; color: var(--text-secondary);">${escapeHTML(commit.author)} · ${formatTimeSince(new Date(commit.date).getTime())}</span>
                                    </div>
                                    <div style="font-size: 0.875rem;">${escapeHTML(commit.message.split('\n')[0])}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div>
                        <h4 style="margin-bottom: 0.5rem; font-size: 1rem;">Files Changed (${pr.files.length})</h4>
                        <div style="max-height: 400px; overflow-y: auto;">
                            ${pr.files.map(file => `
                                <div style="margin-bottom: 1rem; border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                                    <div style="padding: 0.75rem; background: rgba(255,255,255,0.02); display: flex; align-items: center; justify-content: space-between;">
                                        <code style="font-size: 0.875rem;">${escapeHTML(file.filename)}</code>
                                        <div style="display: flex; gap: 0.5rem; font-size: 0.75rem;">
                                            <span style="color: var(--success);">+${file.additions}</span>
                                            <span style="color: #ef4444;">-${file.deletions}</span>
                                        </div>
                                    </div>
                                    ${file.patch ? `
                                        <pre style="margin: 0; padding: 1rem; background: rgba(0,0,0,0.3); overflow-x: auto; font-size: 0.75rem; line-height: 1.5; max-height: 300px;"><code>${escapeHTML(file.patch)}</code></pre>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Append to the page
        detailContainer.insertAdjacentHTML('beforeend', prDetailsHTML);
        
        // Scroll to PR details
        document.querySelector('.card:last-child').scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        hideLoading();
        showToast('Failed to load PR details: ' + error.message, 'error');
    }
}
