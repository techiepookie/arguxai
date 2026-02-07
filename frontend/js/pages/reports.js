/**
 * Reports Page - Funnel Analytics
 */

router.register('/reports', async function () {
    await loadReportsPage();
});

async function loadReportsPage() {
    const view = document.getElementById('app-view');
    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Funnel Analytics</h1>
                <p class="text-secondary">Performance metrics and conversion insights</p>
            </div>
            <div class="header-actions">
                <select class="form-select" onchange="loadFunnelReport(this.value)" id="funnel-selector" style="width: 250px;">
                    <option value="">Select a funnel...</option>
                </select>
            </div>
        </div>
        
        <div id="report-content">
            <div class="card">
                <div class="text-center p-5">
                    <p class="text-muted">Select a funnel to view analytics</p>
                </div>
            </div>
        </div>
    `;
    
    await loadFunnelSelector();
}

async function loadFunnelSelector() {
    try {
        const funnels = await api.listFunnels();
        const selector = document.getElementById('funnel-selector');
        
        if (funnels && funnels.length > 0) {
            selector.innerHTML = '<option value="">Select a funnel...</option>' +
                funnels.map(f => `<option value="${f.id}">${escapeHTML(f.name)}</option>`).join('');
            
            // Auto-select first funnel
            if (funnels.length > 0) {
                selector.value = funnels[0].id;
                await loadFunnelReport(funnels[0].id);
            }
        }
    } catch (error) {
        console.error('Failed to load funnels:', error);
    }
}

async function loadFunnelReport(funnelId) {
    if (!funnelId) return;
    
    const container = document.getElementById('report-content');
    container.innerHTML = '<div class="card"><div class="text-center p-3">Loading analytics...</div></div>';
    
    try {
        const funnel = await api.getFunnel(funnelId);
        
        // Get metrics for each step
        const stepMetrics = await Promise.all(
            funnel.steps.map(async (step, index) => {
                // Simulate metrics - in production, call actual metrics API
                const baseConversion = 100 - (index * 15);
                return {
                    ...step,
                    sessions: Math.floor(1000 - (index * 200)),
                    conversion_rate: baseConversion,
                    drop_rate: index > 0 ? 15 : 0
                };
            })
        );
        
        container.innerHTML = `
            <div class="stats-grid" style="margin-bottom: 1.5rem;">
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-info">
                            <div class="label">Total Sessions</div>
                            <div class="value">${formatNumber(stepMetrics[0].sessions)}</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-info">
                            <div class="label">Overall Conversion</div>
                            <div class="value">${stepMetrics[stepMetrics.length - 1].conversion_rate.toFixed(1)}%</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-info">
                            <div class="label">Completed</div>
                            <div class="value">${formatNumber(stepMetrics[stepMetrics.length - 1].sessions)}</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-info">
                            <div class="label">Drop-off Rate</div>
                            <div class="value trend negative">${((1 - stepMetrics[stepMetrics.length - 1].conversion_rate / 100) * 100).toFixed(1)}%</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">${escapeHTML(funnel.name)} - Step Analysis</h2>
                </div>
                <div class="funnel-container">
                    ${stepMetrics.map((step, index) => `
                        <div class="funnel-step">
                            <div class="step-info">
                                <span class="step-name">
                                    <span style="color: var(--text-muted); font-size: 0.75rem; margin-right: 0.5rem;">Step ${step.order}</span>
                                    ${escapeHTML(step.name)}
                                </span>
                                <span class="step-stats">
                                    ${formatNumber(step.sessions)} sessions
                                    <span class="step-perc">${step.conversion_rate.toFixed(1)}%</span>
                                </span>
                            </div>
                            <div class="step-bar-bg">
                                <div class="step-bar-fill" style="width: ${step.conversion_rate}%"></div>
                            </div>
                            ${index > 0 && step.drop_rate > 0 ? `
                                <div style="font-size: 0.75rem; color: var(--danger); margin-top: 0.25rem;">
                                    ↓ ${step.drop_rate}% drop from previous step
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="card" style="margin-top: 1.5rem;">
                <div class="card-header">
                    <h2 class="card-title">Event Types</h2>
                </div>
                <div class="table">
                    <table style="width: 100%;">
                        <thead>
                            <tr>
                                <th style="color: var(--text-secondary); padding: 1rem;">Step</th>
                                <th style="color: var(--text-secondary); padding: 1rem;">Event Type</th>
                                <th style="color: var(--text-secondary); padding: 1rem;">Sessions</th>
                                <th style="color: var(--text-secondary); padding: 1rem;">Conversion</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stepMetrics.map(step => `
                                <tr style="border-bottom: 1px solid var(--border);">
                                    <td style="padding: 1rem;">${escapeHTML(step.name)}</td>
                                    <td style="padding: 1rem;">
                                        <span class="badge" style="background: rgba(255,255,255,0.05); color: var(--primary);">
                                            ${step.event_type}
                                        </span>
                                    </td>
                                    <td style="padding: 1rem;">${formatNumber(step.sessions)}</td>
                                    <td style="padding: 1rem;">${step.conversion_rate.toFixed(1)}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
    } catch (error) {
        container.innerHTML = `
            <div class="card">
                <div class="text-center p-3 text-danger">Failed to load report: ${error.message}</div>
            </div>
        `;
    }
}
