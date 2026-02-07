/**
 * ArguxAI Premium Dashboard
 * High-performance analytics with real-time anomaly detection
 */

router.register('/dashboard', async function () {
    const view = document.getElementById('app-view');
    const alertContainer = document.getElementById('top-alert-container');

    // Initial skeleton/loading view
    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Dashboard</h1>
                <p class="text-secondary">Monitor your application health and performance</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-outline">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    Last 24 hours
                </button>
            </div>
        </div>
        
        <div class="stats-grid" id="dashboard-hero-stats">
            <!-- Metric cards will be rendered here -->
            <div class="stat-card">Loading...</div>
            <div class="stat-card">Loading...</div>
            <div class="stat-card">Loading...</div>
            <div class="stat-card">Loading...</div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Conversion Funnel</h2>
                    <a href="#/funnels" class="view-all">View Details</a>
                </div>
                <div class="funnel-container" id="dashboard-funnel">
                    <!-- Funnel steps will be rendered here -->
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Recent Issues</h2>
                    <a href="#/issues" class="view-all">View All</a>
                </div>
                <div class="issues-list" id="dashboard-issues">
                    <!-- Issues list will be rendered here -->
                </div>
            </div>
        </div>
    `;

    try {
        const metrics = await api.getDashboardMetrics();

        // 1. Render Top Alert Banner
        renderAlertBanner(metrics.top_alert, alertContainer);

        // 2. Render Hero Cards
        renderHeroCards(metrics);

        // 3. Render Funnel
        renderFunnel(metrics.funnel_steps);

        // 4. Render Issues
        renderIssues(metrics.recent_issues);

    } catch (error) {
        console.error('Dashboard Load Error:', error);
        showToast('Failed to load dashboard data: ' + error.message, 'error');
    }
});

function renderAlertBanner(alert, container) {
    if (!alert) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = `
        <div class="alert-banner ${alert.type}">
            <div class="alert-content">
                <div class="alert-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                </div>
                <div class="alert-text">
                    <h4>${escapeHTML(alert.message)}</h4>
                    <p>${escapeHTML(alert.subtext || '')}</p>
                </div>
            </div>
            <button class="btn btn-primary" onclick="window.location.hash='#/issues'">View Details</button>
        </div>
    `;
}

function renderHeroCards(metrics) {
    const container = document.getElementById('dashboard-hero-stats');
    const cards = [
        { label: 'Total Events', data: metrics.total_events, icon: 'M13 2L3 14h9l-1 8 10-12h-9l1-8z' },
        { label: 'Active Funnels', data: metrics.active_funnels, icon: 'M3 3h18v4L12 16 3 7V3z' },
        { label: 'Error Rate', data: metrics.error_rate, icon: 'M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z' },
        { label: 'Active Users', data: metrics.active_users, icon: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2' }
    ];

    container.innerHTML = cards.map(card => `
        <div class="stat-card">
            <div class="stat-header">
                <div class="stat-info">
                    <div class="label">${card.label}</div>
                    <div class="value">${card.data.current_value}</div>
                </div>
                <div class="stat-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="${card.icon}"></path>
                    </svg>
                </div>
            </div>
            <div class="stat-footer">
                <div class="trend ${card.data.is_positive ? 'positive' : 'negative'}">
                    ${card.data.is_positive ? '↑' : '↓'} ${Math.abs(card.data.change_percentage)}%
                </div>
                <div class="sparkline-container">
                    ${renderSparkline(card.data.sparkline_data, card.data.is_positive)}
                </div>
            </div>
        </div>
    `).join('');
}

function renderSparkline(data, isPositive) {
    if (!data || data.length === 0) return '';
    const points = data.map((d, i) => `${(i / (data.length - 1)) * 100},${100 - (d / Math.max(...data)) * 80}`).join(' ');
    const color = isPositive ? 'var(--success)' : 'var(--danger)';
    return `
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style="width: 100%; height: 100%;">
            <polyline fill="none" stroke="${color}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" points="${points}" />
        </svg>
    `;
}

function renderFunnel(steps) {
    const container = document.getElementById('dashboard-funnel');
    if (!steps || steps.length === 0) {
        container.innerHTML = '<p class="text-muted">No funnel data available</p>';
        return;
    }

    container.innerHTML = steps.map(step => `
        <div class="funnel-step">
            <div class="step-info">
                <span class="step-name">${escapeHTML(step.name)}</span>
                <span class="step-stats">
                    ${formatNumber(step.count)} <span class="step-perc">${formatPercent(step.conversion_rate)}</span>
                </span>
            </div>
            <div class="step-bar-bg">
                <div class="step-bar-fill" style="width: ${step.conversion_rate}%"></div>
            </div>
        </div>
    `).join('');
}

function renderIssues(issues) {
    const container = document.getElementById('dashboard-issues');
    if (!issues || issues.length === 0) {
        container.innerHTML = '<p class="text-muted">No issues detected</p>';
        return;
    }

    container.innerHTML = issues.map(issue => `
        <div class="issue-item">
            <div class="issue-main">
                <div class="issue-meta">
                    <span class="issue-id">ISS-${issue.id.slice(0, 4).toUpperCase()}</span>
                    <span class="badge badge-${issue.severity.toLowerCase()}">${issue.severity}</span>
                </div>
                <div class="issue-title">${escapeHTML(issue.funnel_step)} Performance Drop</div>
                <div class="issue-details">${formatNumber(1523)} events · ${formatTimeSince(issue.detected_at)}</div>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--text-muted)">
                <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
        </div>
    `).join('');
}

