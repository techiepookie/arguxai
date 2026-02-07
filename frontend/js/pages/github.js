/**
 * GitHub Page - PR Management
 */

router.register('/github', async function () {
    await loadGitHubPage();
});

// Make loadPRDetail globally accessible for dynamic routing
window.loadPRDetail = loadPRDetail;

async function loadGitHubPage() {
    const view = document.getElementById('app-view');
    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">GitHub Integration</h1>
                <p class="text-secondary">Auto-generated pull requests for detected issues</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Recent Pull Requests</h2>
            </div>
            <div id="github-prs-list">
                <div class="text-center p-3">Loading PRs...</div>
            </div>
        </div>
        
        <!-- PR Detail Modal -->
        <div id="pr-detail-modal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.9); z-index: 1000; overflow-y: auto; padding: 2rem;">
            <div style="max-width: 1200px; margin: 0 auto; background: var(--card-bg); border-radius: 12px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem;">
                    <h2 style="margin: 0; color: var(--text-primary); font-size: 1.5rem;">Pull Request Details</h2>
                    <button onclick="closePRDetail()" style="background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 2rem; line-height: 1; padding: 0; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 4px; transition: all 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">&times;</button>
                </div>
                <div id="pr-detail-content"></div>
            </div>
        </div>
    `;
    
    await loadPRsList();
}

async function loadPRsList() {
    const container = document.getElementById('github-prs-list');
    
    try {
        // Fetch PRs from GitHub API
        const response = await api.request('/api/github/prs?repository=techiepookie/demo-login-app');
        const prs = response.prs || [];
        
        if (prs.length === 0) {
            container.innerHTML = `
                <div class="text-center p-5">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" style="color: var(--text-muted); margin-bottom: 1rem;">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                    </svg>
                    <p class="text-muted">No PRs generated yet.</p>
                    <p class="text-secondary" style="font-size: 0.875rem;">Go to Issues page and generate PRs for detected anomalies.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = prs.map(pr => `
            <div class="issue-item" onclick="loadPRDetail(${pr.number})" style="cursor: pointer;">
                <div class="issue-main">
                    <div class="issue-meta">
                        <span class="badge" style="background: rgba(6, 182, 212, 0.1); color: var(--primary);">PR #${pr.number}</span>
                        <span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">${pr.state}</span>
                    </div>
                    <div class="issue-title" style="font-size: 1.125rem; margin-top: 0.5rem;">
                        ${escapeHTML(pr.title)}
                    </div>
                    <div class="issue-details" style="font-size: 0.875rem; margin-top: 0.25rem;">
                        Branch: ${escapeHTML(pr.branch)} · Created by ${escapeHTML(pr.user)} · ${formatTimeSince(new Date(pr.created_at).getTime())}
                    </div>
                </div>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--text-muted)">
                    <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load PRs:', error);
        container.innerHTML = '<div class="text-center p-3 text-danger">Failed to load PRs: ' + error.message + '</div>';
    }
}

async function loadPRDetail(prNumber) {
    const modal = document.getElementById('pr-detail-modal');
    const content = document.getElementById('pr-detail-content');
    
    modal.style.display = 'block';
    content.innerHTML = '<div class="text-center p-3">Loading PR details...</div>';
    
    try {
        const pr = await api.request(`/api/github/prs/${prNumber}?repository=techiepookie/demo-login-app`);
        
        content.innerHTML = `
            <div style="margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <span class="badge" style="background: rgba(6, 182, 212, 0.1); color: var(--primary); font-size: 1rem;">PR #${pr.number}</span>
                    <span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success); font-size: 1rem;">${pr.state}</span>
                    <a href="${pr.url}" target="_blank" class="btn btn-outline" style="margin-left: auto;">
                        View on GitHub →
                    </a>
                </div>
                <h3 style="margin: 0.5rem 0;">${escapeHTML(pr.title)}</h3>
                <div style="color: var(--text-secondary); font-size: 0.875rem;">
                    ${escapeHTML(pr.user.login)} wants to merge ${pr.commits} commit${pr.commits !== 1 ? 's' : ''} into <code>${pr.base_branch}</code> from <code>${pr.branch}</code>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem;">
                <div style="padding: 1rem; background: rgba(16, 185, 129, 0.05); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Additions</div>
                    <div style="font-size: 1.5rem; color: var(--success); font-weight: 600;">+${pr.additions}</div>
                </div>
                <div style="padding: 1rem; background: rgba(239, 68, 68, 0.05); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Deletions</div>
                    <div style="font-size: 1.5rem; color: #ef4444; font-weight: 600;">-${pr.deletions}</div>
                </div>
                <div style="padding: 1rem; background: rgba(6, 182, 212, 0.05); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Files Changed</div>
                    <div style="font-size: 1.5rem; color: var(--primary); font-weight: 600;">${pr.changed_files}</div>
                </div>
            </div>
            
            ${pr.body ? `
                <div style="margin-bottom: 2rem;">
                    <h4 style="margin-bottom: 0.5rem;">Description</h4>
                    <div style="padding: 1rem; background: rgba(255,255,255,0.02); border-radius: 8px; white-space: pre-wrap; font-size: 0.875rem; line-height: 1.6;">
${escapeHTML(pr.body)}</div>
                </div>
            ` : ''}
            
            <div style="margin-bottom: 2rem;">
                <h4 style="margin-bottom: 0.5rem;">Commits (${pr.commits})</h4>
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
            
            <div>
                <h4 style="margin-bottom: 0.5rem;">Files Changed (${pr.files.length})</h4>
                ${pr.files.map(file => `
                    <div style="margin-bottom: 1.5rem; border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                        <div style="padding: 0.75rem; background: rgba(255,255,255,0.02); display: flex; align-items: center; justify-content: space-between;">
                            <code style="font-size: 0.875rem;">${escapeHTML(file.filename)}</code>
                            <div style="display: flex; gap: 0.5rem; font-size: 0.75rem;">
                                <span style="color: var(--success);">+${file.additions}</span>
                                <span style="color: #ef4444;">-${file.deletions}</span>
                            </div>
                        </div>
                        ${file.patch ? `
                            <pre style="margin: 0; padding: 1rem; background: rgba(0,0,0,0.2); overflow-x: auto; font-size: 0.75rem; line-height: 1.5;"><code>${escapeHTML(file.patch)}</code></pre>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Failed to load PR details:', error);
        content.innerHTML = '<div class="text-center p-3 text-danger">Failed to load PR details: ' + error.message + '</div>';
    }
}

function closePRDetail() {
    document.getElementById('pr-detail-modal').style.display = 'none';
}
