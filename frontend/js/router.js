/**
 * Client-side router for SPA navigation
 */

class Router {
    constructor() {
        this.routes = {};
        this.currentPage = null;

        // Listen for hash changes
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());
    }

    // Register a route
    register(path, handler) {
        this.routes[path] = handler;
    }

    // Navigate to a route
    navigate(path) {
        window.location.hash = path;
    }

    // Handle route change
    async handleRoute() {
        const hash = window.location.hash.slice(1) || '/dashboard';
        const route = hash.split('?')[0];

        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            const page = item.getAttribute('data-page');
            if (`/${page}` === route || route.startsWith(`/${page}/`)) {
                item.classList.add('active');
            }
        });

        // Check for dynamic routes (e.g., /issues/:id)
        let handler = this.routes[route];
        
        // If exact match not found, check for dynamic routes
        if (!handler) {
            // Check if it's an issue detail route
            if (route.startsWith('/issues/')) {
                const issueId = route.split('/')[2];
                if (issueId) {
                    // Call the issue detail handler
                    const issuesPage = await import('./pages/issues.js');
                    if (window.loadIssueDetail) {
                        this.currentPage = route;
                        await window.loadIssueDetail(issueId);
                        return;
                    }
                }
            }
            
            // Fall back to 404
            handler = this.routes['/404'];
        }
        
        if (handler) {
            this.currentPage = route;
            await handler();
        }
    }
}

// Global router instance
const router = new Router();

// Register 404 handler
router.register('/404', () => {
    document.getElementById('app-view').innerHTML = `
        <div class="page-header">
            <h1 class="page-title">Page Not Found</h1>
            <p class="page-subtitle">The page you're looking for doesn't exist.</p>
        </div>
    `;
});
