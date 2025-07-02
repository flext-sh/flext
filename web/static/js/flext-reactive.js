// FLEXT Reactive JavaScript with Alpine.js and Chart.js

// Chart.js configuration and management
const chartInstances = new Map();

// Alpine.js chart component
function chart(chartId, chartType) {
    return {
        chart: null,

        initChart() {
            const ctx = document.getElementById(chartId);
            if (!ctx) return;

            // Create chart based on type
            const config = this.getChartConfig(chartType);
            this.chart = new Chart(ctx, config);
            chartInstances.set(chartId, this.chart);

            // Load initial data
            this.loadChartData();
        },

        getChartConfig(type) {
            const baseConfig = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            };

            switch (type) {
                case 'doughnut':
                    return {
                        type: 'doughnut',
                        data: {
                            labels: [],
                            datasets: []
                        },
                        options: baseConfig
                    };
                case 'line':
                    return {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: []
                        },
                        options: {
                            ...baseConfig,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    };
                default:
                    return {
                        type: 'bar',
                        data: {
                            labels: [],
                            datasets: []
                        },
                        options: baseConfig
                    };
            }
        },

        async loadChartData() {
            try {
                const response = await fetch(`/api/charts/${chartId}/data`);
                if (response.ok) {
                    const data = await response.json();
                    this.updateChart(data);
                }
            } catch (error) {
                console.error('Error loading chart data:', error);
            }
        },

        updateChart(data) {
            if (this.chart) {
                this.chart.data = data;
                this.chart.update('active');
            }
        }
    }
}

// Global chart update function for HTMX
function updateChart(response) {
    try {
        const data = JSON.parse(response);
        const chartId = data.chartId || 'overviewChart';
        const chart = chartInstances.get(chartId);
        if (chart) {
            chart.data = data;
            chart.update('active');
        }
    } catch (error) {
        console.error('Error updating chart:', error);
    }
}

// HTMX event listeners for enhanced interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to HTMX requests
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        const target = evt.target;
        if (target.hasAttribute('hx-indicator')) {
            const indicator = document.querySelector(target.getAttribute('hx-indicator'));
            if (indicator) {
                indicator.style.display = 'block';
            }
        }
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        const target = evt.target;
        if (target.hasAttribute('hx-indicator')) {
            const indicator = document.querySelector(target.getAttribute('hx-indicator'));
            if (indicator) {
                indicator.style.display = 'none';
            }
        }
    });

    // Add error handling
    document.body.addEventListener('htmx:responseError', function(evt) {
        showNotification('Error loading data. Please try again.', 'error');
    });

    // Add success notifications
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // Add smooth transitions to new content
        const newContent = evt.target;
        newContent.style.opacity = '0';
        newContent.style.transform = 'translateY(10px)';

        requestAnimationFrame(() => {
            newContent.style.transition = 'all 0.3s ease';
            newContent.style.opacity = '1';
            newContent.style.transform = 'translateY(0)';
        });
    });
});

// Notification system
<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/2.4.0/purify.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/2.4.0/purify.min.js"></script>
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;

    const colors = {
        info: 'bg-blue-500 text-white',
        success: 'bg-green-500 text-white',
        warning: 'bg-yellow-500 text-black',
        error: 'bg-red-500 text-white'
    };

    notification.className += ` ${colors[type] || colors.info}`;
    notification.innerHTML = `
        <div class="flex items-center">
            <span>${DOMPurify.sanitize(message)}</span>
            <button class="ml-4 text-lg" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;

    document.body.appendChild(notification);

    // Slide in
    requestAnimationFrame(() => {
        notification.style.transform = 'translateX(0)';
    });

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(full)';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Enhanced Alpine.js components
function dashboard() {
    return {
        stats: {
            pipelines: 0,
            plugins: 0,
            activeJobs: 0,
            systemStatus: 'checking'
        },
        loading: true,

        init() {
            this.loadStats();
            // Auto-refresh every 30 seconds
            setInterval(() => this.loadStats(), 30000);
        },

        async loadStats() {
            try {
                this.loading = true;
                const response = await fetch('/api/dashboard/stats');
                if (response.ok) {
                    this.stats = await response.json();
                    this.$dispatch('stats-updated', this.stats);
                }
            } catch (error) {
                console.error('Error loading stats:', error);
                showNotification('Error loading dashboard stats', 'error');
            } finally {
                this.loading = false;
            }
        }
    }
}

// Form handling with validation
function form(action, method) {
    return {
        submitting: false,
        errors: {},

        async submit(formData) {
            this.submitting = true;
            this.errors = {};

            try {
                const response = await fetch(action, {
                    method: method.toUpperCase(),
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    showNotification('Operation completed successfully!', 'success');
                    this.$dispatch('form-success', { response });
                } else {
                    const errorData = await response.json();
                    this.errors = errorData.errors || {};
                    showNotification(errorData.message || 'An error occurred', 'error');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                showNotification('Network error. Please try again.', 'error');
            } finally {
                this.submitting = false;
            }
        }
    }
}

// Real-time monitoring component
function monitor() {
    return {
        metrics: {
            cpu: 0,
            memory: 0,
            connections: 0,
            uptime: '0d 0h 0m'
        },
        alerts: [],

        init() {
            this.startMonitoring();
        },

        startMonitoring() {
            // Simulate real-time data
            setInterval(() => {
                this.updateMetrics();
            }, 5000);
        },

        updateMetrics() {
            // Simulate fluctuating metrics
            this.metrics.cpu = Math.floor(Math.random() * 100);
            this.metrics.memory = Math.floor(Math.random() * 100);
            this.metrics.connections = Math.floor(Math.random() * 50);

            // Check for alerts
            this.checkAlerts();
        },

        checkAlerts() {
            if (this.metrics.cpu > 90) {
                this.addAlert('High CPU usage detected', 'warning');
            }
            if (this.metrics.memory > 85) {
                this.addAlert('High memory usage detected', 'warning');
            }
        },

        addAlert(message, type) {
            const alert = {
                id: Date.now(),
                message,
                type,
                timestamp: new Date().toLocaleTimeString()
            };

            this.alerts.unshift(alert);
            // Keep only last 10 alerts
            if (this.alerts.length > 10) {
                this.alerts = this.alerts.slice(0, 10);
            }

            showNotification(message, type);
        }
    }
}

// Quick actions
function createPipeline() {
    showNotification('Opening pipeline creation form...', 'info');
    // This would typically open a modal or navigate to a form
}

function registerPlugin() {
    showNotification('Opening plugin registration form...', 'info');
    // This would typically open a modal or navigate to a form
}

function runDiagnostics() {
    showNotification('Running system diagnostics...', 'info');

    // Simulate diagnostics
    setTimeout(() => {
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'healthy') {
                    showNotification('System diagnostics passed!', 'success');
                } else {
                    showNotification('System diagnostics found issues', 'warning');
                }
            })
            .catch(() => {
                showNotification('Diagnostics failed', 'error');
            });
    }, 2000);
}

// Utility functions
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
}

// Export functions for global use
window.chart = chart;
window.dashboard = dashboard;
window.form = form;
window.monitor = monitor;
window.createPipeline = createPipeline;
window.registerPlugin = registerPlugin;
window.runDiagnostics = runDiagnostics;
window.showNotification = showNotification;
window.updateChart = updateChart;
