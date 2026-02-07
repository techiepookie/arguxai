/**
 * ArguxAI Funnels Page
 * Manual builder + AI-powered funnel generation
 */

let currentView = 'list'; // list, create, create-ai, edit
let currentFunnelId = null;

router.register('/funnels', async function () {
    await loadFunnelsList();
});

async function loadFunnelsList() {
    const view = document.getElementById('app-view');
    currentView = 'list';

    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Funnels</h1>
                <p class="text-secondary">Manage conversion funnels and track user journeys</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-outline" onclick="showCreateManualFunnel()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Manual Builder
                </button>
                <button class="btn btn-primary" onclick="showCreateAIFunnel()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7v10l10 5 10-5V7L12 2z"/>
                    </svg>
                    AI Generate
                </button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">All Conversion Funnels</h2>
            </div>
            <div id="funnels-list">
                <div class="text-center p-3">Loading funnels...</div>
            </div>
        </div>
    `;

    try {
        const funnels = await api.listFunnels();
        const listContainer = document.getElementById('funnels-list');

        if (!funnels || funnels.length === 0) {
            listContainer.innerHTML = `
                <div class="text-center p-5">
                    <p class="text-muted">No funnels yet. Start by creating one manually or using AI.</p>
                </div>
            `;
            return;
        }

        listContainer.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th style="color: var(--text-secondary)">Name</th>
                        <th style="color: var(--text-secondary)">Steps</th>
                        <th style="color: var(--text-secondary)">Source</th>
                        <th style="color: var(--text-secondary)">Created</th>
                        <th style="color: var(--text-secondary)">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${funnels.map(funnel => `
                        <tr>
                            <td>
                                <strong style="color: white; font-size: 1rem;">${escapeHTML(funnel.name)}</strong>
                                <div style="font-size: 0.75rem; color: var(--text-muted);">${escapeHTML(funnel.description || 'No description')}</div>
                            </td>
                            <td>
                                <span class="badge" style="background: rgba(255,255,255,0.05); color: var(--text-secondary)">
                                    ${funnel.steps.length} steps
                                </span>
                            </td>
                            <td>
                                ${funnel.created_by_ai ?
                '<span class="badge" style="background: rgba(6, 182, 212, 0.1); color: var(--primary);">AI GEN</span>' :
                '<span class="badge" style="background: rgba(255,255,255,0.05); color: var(--text-muted);">MANUAL</span>'}
                            </td>
                            <td style="font-size: 0.875rem; color: var(--text-secondary)">${formatDate(funnel.created_at)}</td>
                            <td>
                                <div class="header-actions">
                                    <button class="btn btn-outline" style="padding: 0.4rem 0.75rem; font-size: 0.75rem;" 
                                            onclick="editFunnel('${funnel.id}')">Edit</button>
                                    <button class="btn btn-outline" style="padding: 0.4rem 0.75rem; font-size: 0.75rem; color: var(--danger); border-color: rgba(239, 68, 68, 0.2);" 
                                            onclick="deleteFunnel('${funnel.id}', '${escapeHTML(funnel.name)}')">Delete</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        document.getElementById('funnels-list').innerHTML = `<div class="text-center p-3 text-danger">Failed to load funnels.</div>`;
    }
}

function showCreateManualFunnel() {
    const view = document.getElementById('app-view');
    currentView = 'create';

    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Create Manual Funnel</h1>
                <p class="text-secondary">Define your conversion funnel step by step</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-outline" onclick="loadFunnelsList()">Back to List</button>
            </div>
        </div>
        
        <div class="card" style="max-width: 800px;">
            <form id="manual-funnel-form" onsubmit="handleManualFunnelSubmit(event)">
                <div class="form-group">
                    <label class="form-label">Funnel Name *</label>
                    <input type="text" class="form-input" id="funnel-name" required 
                           placeholder="e.g., Checkout Flow v2" />
                </div>
                
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea class="form-textarea" id="funnel-description" 
                              placeholder="Track user journey from cart to success"></textarea>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Funnel Steps *</label>
                    <div id="steps-container">
                        <div class="step-item" data-order="1">
                            <input type="text" class="form-input" placeholder="Step Name" required />
                            <select class="form-select">
                                <option value="page_view">Page View</option>
                                <option value="button_click">Button Click</option>
                                <option value="form_submit">Form Submit</option>
                                <option value="custom">Custom Event</option>
                            </select>
                        </div>
                    </div>
                    <button type="button" class="btn btn-outline mt-2" onclick="addStep()">+ Add Step</button>
                </div>
                
                <div class="header-actions mt-3">
                    <button type="submit" class="btn btn-primary">Create Funnel</button>
                    <button type="button" class="btn btn-outline" onclick="loadFunnelsList()">Cancel</button>
                </div>
            </form>
        </div>
    `;
}

function addStep() {
    const container = document.getElementById('steps-container');
    const order = container.children.length + 1;
    const stepDiv = document.createElement('div');
    stepDiv.className = 'step-item';
    stepDiv.setAttribute('data-order', order);
    stepDiv.innerHTML = `
        <input type="text" class="form-input" placeholder="Step Name" required />
        <select class="form-select">
            <option value="page_view">Page View</option>
            <option value="button_click">Button Click</option>
            <option value="form_submit">Form Submit</option>
            <option value="custom">Custom Event</option>
        </select>
        <button type="button" class="btn btn-outline" onclick="this.parentElement.remove()" style="padding: 0.5rem; color: var(--danger); border-color: rgba(239, 68, 68, 0.2);">×</button>
    `;
    container.appendChild(stepDiv);
}

async function handleManualFunnelSubmit(event) {
    event.preventDefault();
    const name = document.getElementById('funnel-name').value;
    const description = document.getElementById('funnel-description').value;

    const stepsContainer = document.getElementById('steps-container');
    const stepItems = stepsContainer.querySelectorAll('.step-item');
    const steps = Array.from(stepItems).map((item, index) => ({
        name: item.querySelector('input').value,
        event_type: item.querySelector('select').value,
        order: index + 1
    }));

    const funnelData = {
        name,
        description: description || null,
        steps,
        created_by_ai: false
    };

    try {
        // Instant feedback for manual creation
        const btn = event.target.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Creating...';
        btn.disabled = true;

        await api.createFunnel(funnelData);

        showToast('Funnel created!', 'success');
        await loadFunnelsList();
    } catch (error) {
        // Reset button state on error
        const btn = event.target.querySelector('button[type="submit"]');
        if (btn) {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
        showToast('Error: ' + error.message, 'error');
    }
}

function showCreateAIFunnel() {
    const view = document.getElementById('app-view');
    currentView = 'create-ai';

    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">AI Funnel Architect</h1>
                <p class="text-secondary">AI generates optimized funnel structures based on your requirements</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-outline" onclick="loadFunnelsList()">Back to List</button>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <div class="form-group">
                    <label class="form-label">Requirement Specification</label>
                    <textarea class="form-textarea" id="ai-prompt" 
                              placeholder="e.g., Build a multi-step signup funnel for a mobile banking app including KYC and card order steps."
                              style="min-height: 200px; font-family: monospace; font-size: 0.875rem;"></textarea>
                </div>
                
                <div class="header-actions">
                    <button class="btn btn-outline" onclick="handleEnhancePrompt()">
                        ✨ Optimize Prompt
                    </button>
                    <button class="btn btn-primary" onclick="handleGenerateFunnel()">
                        🤖 Generate System
                    </button>
                </div>

                <div id="ai-improvements-area" style="margin-top: 1.5rem;"></div>
            </div>
            
            <div id="ai-result-area">
                <div class="card" style="display: flex; align-items: center; justify-content: center; min-height: 300px; border-style: dashed; opacity: 0.5;">
                    <div class="text-center">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color: var(--primary); margin-bottom: 1rem;">
                            <path d="M12 2L2 7v10l10 5 10-5V7L12 2z"/>
                        </svg>
                        <p class="text-muted">AI Output Preview Area</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function handleEnhancePrompt() {
    const prompt = document.getElementById('ai-prompt').value.trim();
    if (!prompt) return showToast('Prompt required', 'warning');

    try {
        showLoading();
        const result = await api.enhancePrompt(prompt);
        hideLoading();

        document.getElementById('ai-prompt').value = result.enhanced_prompt;

        if (result.improvements && result.improvements.length > 0) {
            document.getElementById('ai-improvements-area').innerHTML = `
                <div style="font-size: 0.75rem; color: var(--primary); font-weight: 600; text-transform: uppercase;">Improvements Made:</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                    ${result.improvements.map(imp => `• ${escapeHTML(imp)}`).join('<br>')}
                </div>
            `;
        }
        showToast('Prompt optimized!', 'success');
    } catch (error) {
        hideLoading();
        showToast('Optimization failed: ' + error.message, 'error');
    }
}

async function handleGenerateFunnel() {
    const prompt = document.getElementById('ai-prompt').value.trim();
    
    // Validate prompt
    if (!prompt) {
        showToast('Please enter a prompt', 'warning');
        return;
    }
    
    if (prompt.length < 10) {
        showToast('Prompt is too short. Please provide more details about your funnel requirements.', 'error');
        return;
    }
    
    // Check if prompt is valid (contains funnel-related keywords)
    const funnelKeywords = ['funnel', 'flow', 'journey', 'conversion', 'signup', 'checkout', 'onboarding', 'registration', 'purchase', 'user', 'step', 'process'];
    const hasValidKeyword = funnelKeywords.some(keyword => prompt.toLowerCase().includes(keyword));
    
    if (!hasValidKeyword) {
        showToast('Invalid prompt: Please describe a user funnel or conversion flow. Include keywords like "funnel", "flow", "signup", "checkout", etc.', 'error');
        return;
    }

    try {
        showLoading();
        const result = await api.generateAIFunnel(prompt);
        hideLoading();
        
        // Check if API returned valid funnel
        if (!result || !result.funnel || !result.funnel.steps || result.funnel.steps.length === 0) {
            showToast('Unable to generate funnel from this prompt. Please provide more specific details about the user flow.', 'error');
            return;
        }

        const funnel = result.funnel;
        const resultArea = document.getElementById('ai-result-area');

        resultArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Generated Architecture</h3>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <strong style="font-size: 1.125rem; color: white;">${escapeHTML(funnel.name)}</strong>
                    <div class="text-secondary" style="font-size: 0.875rem; margin-top: 0.5rem;">${escapeHTML(funnel.description || '')}</div>
                </div>
                
                <div class="funnel-container" style="gap: 0.5rem; margin-bottom: 1.5rem;">
                    ${funnel.steps.map(step => `
                        <div class="issue-item" style="cursor: default;">
                            <div class="issue-main">
                                <span class="issue-id">Step ${step.order}</span>
                                <div class="issue-title">${escapeHTML(step.name)}</div>
                            </div>
                            <span class="badge" style="background: rgba(255,255,255,0.05); color: var(--primary)">${step.event_type}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div style="padding: 1rem; background: rgba(6, 182, 212, 0.05); border: 1px solid var(--primary-glow); border-radius: 8px; margin-bottom: 1.5rem;">
                    <div style="font-size: 0.75rem; color: var(--primary); font-weight: 700; margin-bottom: 0.25rem;">AI REASONING</div>
                    <p style="font-size: 0.8125rem; color: var(--text-secondary);">${escapeHTML(result.reasoning)}</p>
                </div>
                
                <button class="btn btn-primary" style="width: 100%; justify-content: center;"
                        onclick='saveGeneratedFunnel(${JSON.stringify(funnel).replace(/'/g, "&apos;")})'>
                    Finalize and Deploy Funnel
                </button>
            </div>
        `;
        showToast('Generation successful!', 'success');
    } catch (error) {
        hideLoading();
        console.error('Funnel generation error:', error);
        showToast('Unable to generate funnel. Please refine your prompt and try again.', 'error');
    }
}

async function saveGeneratedFunnel(funnel) {
    try {
        showLoading();
        await api.createFunnel(funnel);
        hideLoading();
        showToast('Funnel deployed!', 'success');
        await loadFunnelsList();
    } catch (error) {
        hideLoading();
        showToast('Deployment failed: ' + error.message, 'error');
    }
}

async function deleteFunnel(id, name) {
    if (!confirm(`Delete funnel "${name}"?`)) return;
    try {
        showLoading();
        await api.deleteFunnel(id);
        hideLoading();
        showToast('Funnel deleted', 'success');
        await loadFunnelsList();
    } catch (error) {
        hideLoading();
        showToast('Deletion failed: ' + error.message, 'error');
    }
}

async function editFunnel(id) {
    showToast('Advanced editing in development', 'warning');
}

