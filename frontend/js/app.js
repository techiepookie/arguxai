/**
 * ArguxAI Application Initializer
 * Main app entry point
 */

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    console.log('ArguxAI Dashboard Initialized');

    // Initialize Theme
    const savedTheme = localStorage.getItem('arguxai-theme') || 'dark';
    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
    }

    // Initialize router and load first page
    router.handleRoute();
});

// Toggle Theme Function
window.toggleTheme = function () {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('arguxai-theme', newTheme);

    // Update icon if exists
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.innerHTML = newTheme === 'light' ?
            '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>' : // Moon for Dark
            '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>'; // Sun for Light
    }
};

// Global error handler
window.addEventListener('error', function (e) {
    console.error('Global error:', e.error);
    showToast('An error occurred. Please check console.', 'error');
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function (e) {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('An error occurred. Please check console.', 'error');
});
