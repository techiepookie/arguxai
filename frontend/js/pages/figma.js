/**
 * Figma Page - Design Review
 */

router.register('/figma', async function () {
    await loadFigmaPage();
});

async function loadFigmaPage() {
    const view = document.getElementById('app-view');
    view.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Figma Design Review</h1>
                <p class="text-secondary">AI-powered UI/UX analysis for conversion optimization</p>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Review Figma Design</h2>
                </div>
                <form onsubmit="handleFigmaReview(event)">
                    <div class="form-group">
                        <label class="form-label">Figma File URL</label>
                        <input type="url" id="figma-url" class="form-input" 
                               placeholder="https://www.figma.com/file/..." required />
                        <p class="form-help">Paste the Figma file URL to analyze</p>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Issue Context (Optional)</label>
                        <textarea id="figma-context" class="form-input" 
                                  placeholder="e.g., Users are dropping off at the signup form..."
                                  style="min-height: 100px;"></textarea>
                        <p class="form-help">Provide context about conversion issues</p>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" style="width: 100%;">
                        🎨 Analyze Design
                    </button>
                </form>
            </div>
            
            <div id="figma-results">
                <div class="card" style="display: flex; align-items: center; justify-content: center; min-height: 400px; border-style: dashed; opacity: 0.5;">
                    <div class="text-center">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" style="color: var(--primary); margin-bottom: 1rem;">
                            <path d="M8 24c2.208 0 4-1.792 4-4v-4H8c-2.208 0-4 1.792-4 4s1.792 4 4 4z" />
                            <path d="M4 12c0-2.208 1.792-4 4-4h4v8H8c-2.208 0-4-1.792-4-4z" />
                            <path d="M4 4c0-2.208 1.792-4 4-4h4v8H8C5.792 8 4 6.208 4 4z" />
                            <path d="M12 0h4c2.208 0 4 1.792 4 4s-1.792 4-4 4h-4V0z" />
                            <path d="M20 12c0 2.208-1.792 4-4 4s-4-1.792-4-4 1.792-4 4-4 4 1.792 4 4z" />
                        </svg>
                        <p class="text-muted">Analysis Results Will Appear Here</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-header">
                <h2 class="card-title">Recent Reviews</h2>
            </div>
            <div id="figma-history">
                <div class="text-center p-3 text-muted">No reviews yet. Start by analyzing a Figma design above.</div>
            </div>
        </div>
    `;
}

async function handleFigmaReview(event) {
    event.preventDefault();
    
    const url = document.getElementById('figma-url').value;
    const context = document.getElementById('figma-context').value;
    
    // Extract file key from URL - support multiple formats
    let fileKey = null;
    
    // Try different URL patterns
    const patterns = [
        /file\/([a-zA-Z0-9]+)/,           // Standard: /file/abc123
        /design\/([a-zA-Z0-9]+)/,         // Design: /design/abc123
        /proto\/([a-zA-Z0-9]+)/,          // Prototype: /proto/abc123
        /figma\.com\/([a-zA-Z0-9]+)/      // Direct: figma.com/abc123
    ];
    
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) {
            fileKey = match[1];
            break;
        }
    }
    
    if (!fileKey) {
        showToast('Invalid Figma URL format', 'error');
        return;
    }
    
    try {
        showLoading();
        
        // Call Figma review API
        const response = await fetch('http://localhost:8000/api/figma/review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer demo'
            },
            body: JSON.stringify({
                file_key: fileKey,
                frame_ids: null,
                issue_id: null
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            let errorMsg = errorData.detail || 'Review failed';
            
            // Provide helpful error messages
            if (errorMsg.includes('404')) {
                errorMsg = 'Figma file not found. Please check:\n1. The file URL is correct\n2. Your Figma token has access to this file\n3. The file is not private';
            } else if (errorMsg.includes('401') || errorMsg.includes('403')) {
                errorMsg = 'Figma authentication failed. Please check your Figma access token in .env file';
            } else if (errorMsg.includes('No image URL')) {
                errorMsg = 'Unable to render Figma frames. The file may not have any frames or the API failed to generate images.';
            }
            
            throw new Error(errorMsg);
        }
        
        const result = await response.json();
        hideLoading();
        
        // Display results from analyses array
        if (result.analyses && result.analyses.length > 0) {
            displayFigmaResults(result.analyses[0]);
            showToast('Analysis complete!', 'success');
        } else {
            throw new Error('No analysis results returned');
        }
        
    } catch (error) {
        hideLoading();
        console.error('Figma review error:', error);
        showToast(error.message, 'error');
    }
}

function displayFigmaResults(analysis) {
    const container = document.getElementById('figma-results');
    
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Analysis Results</h2>
                <span class="badge" style="background: rgba(6, 182, 212, 0.1); color: var(--primary);">
                    Score: ${Math.round(analysis.overall_score)}/100
                </span>
            </div>
            
            ${analysis.issues && analysis.issues.length > 0 ? `
                <div style="margin-bottom: 1.5rem;">
                    <div style="font-size: 0.875rem; font-weight: 600; margin-bottom: 0.75rem; color: var(--text-secondary);">
                        ISSUES FOUND (${analysis.issues.length})
                    </div>
                    ${analysis.issues.map(issue => `
                        <div style="padding: 1rem; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; margin-bottom: 0.75rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span class="badge badge-${issue.severity}">${issue.severity}</span>
                                <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">${issue.issue_type.replace(/_/g, ' ')}</span>
                            </div>
                            <div style="font-weight: 600; margin-bottom: 0.25rem;">${escapeHTML(issue.description)}</div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                💡 ${escapeHTML(issue.recommendation)}
                            </div>
                            ${issue.location ? `<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem;">📍 ${escapeHTML(issue.location)}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${analysis.strengths && analysis.strengths.length > 0 ? `
                <div style="margin-bottom: 1.5rem;">
                    <div style="font-size: 0.875rem; font-weight: 600; margin-bottom: 0.75rem; color: var(--text-secondary);">
                        STRENGTHS
                    </div>
                    ${analysis.strengths.map(strength => `
                        <div style="padding: 0.75rem; background: rgba(16, 185, 129, 0.05); border-radius: 8px; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.875rem; color: var(--text-primary);">✓ ${escapeHTML(strength)}</div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${analysis.priority_fixes && analysis.priority_fixes.length > 0 ? `
                <div style="margin-bottom: 1.5rem;">
                    <div style="font-size: 0.875rem; font-weight: 600; margin-bottom: 0.75rem; color: var(--text-secondary);">
                        PRIORITY FIXES
                    </div>
                    ${analysis.priority_fixes.map((fix, i) => `
                        <div style="padding: 0.75rem; background: rgba(6, 182, 212, 0.05); border-left: 3px solid var(--primary); margin-bottom: 0.5rem;">
                            <div style="font-size: 0.875rem; color: var(--text-primary);">${i + 1}. ${escapeHTML(fix)}</div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <div style="padding: 1rem; background: rgba(6, 182, 212, 0.05); border: 1px solid var(--primary-glow); border-radius: 8px;">
                <div style="font-size: 0.75rem; color: var(--primary); font-weight: 700; margin-bottom: 0.5rem;">CONVERSION IMPACT</div>
                <p style="font-size: 0.875rem; color: var(--text-primary); line-height: 1.6;">${escapeHTML(analysis.conversion_impact_assessment)}</p>
            </div>
            
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-muted);">
                Analyzed by ${analysis.model_used} in ${analysis.analysis_time_ms}ms
            </div>
        </div>
    `;
}
