/**
 * API Service - Centralized API calls to ArguxAI backend
 */

const API_BASE = 'http://localhost:8000';
const API_KEY = 'Bearer demo'; // Replace with actual auth

class APIService {
    constructor() {
        this.baseURL = API_BASE;
        this.apiKey = API_KEY;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': this.apiKey,
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'API request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Dashboard
    async getDashboardMetrics() {
        return this.request('/api/dashboard/metrics');
    }

    // Funnels
    async listFunnels() {
        return this.request('/api/funnels');
    }

    async getFunnel(id) {
        return this.request(`/api/funnels/${id}`);
    }

    async createFunnel(data) {
        return this.request('/api/funnels', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateFunnel(id, data) {
        return this.request(`/api/funnels/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteFunnel(id) {
        return this.request(`/api/funnels/${id}`, {
            method: 'DELETE'
        });
    }

    async enhancePrompt(prompt) {
        return this.request('/api/funnels/enhance-prompt', {
            method: 'POST',
            body: JSON.stringify({ prompt })
        });
    }

    async generateAIFunnel(prompt) {
        return this.request('/api/funnels/generate-ai', {
            method: 'POST',
            body: JSON.stringify({ prompt })
        });
    }

    // Issues
    async detectIssues() {
        return this.request('/api/issues/detect', {
            method: 'POST'
        });
    }

    async listIssues() {
        return this.request('/api/issues');
    }

    async getIssue(id) {
        return this.request(`/api/issues/${id}`);
    }

    async diagnoseIssue(id) {
        return this.request(`/api/issues/${id}/diagnose`, {
            method: 'POST'
        });
    }

    // GitHub
    async generatePR(issueId) {
        // Use correct repository path
        const repository = 'techiepookie/demo-login-app';
        const filePath = 'demo-login-app/login.js';
        
        return this.request(`/api/github/generate-pr-simple?issue_id=${issueId}&repository=${encodeURIComponent(repository)}&file_path=${encodeURIComponent(filePath)}`, {
            method: 'POST'
        });
    }

    // Jira
    async createJiraTicket(issueId) {
        return this.request(`/api/jira/create-ticket/${issueId}`, {
            method: 'POST'
        });
    }

    // Events
    async ingestEvents(events) {
        return this.request('/api/events', {
            method: 'POST',
            body: JSON.stringify(events)
        });
    }
}

// Global API instance
const api = new APIService();
