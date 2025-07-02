// FLEXT Web Interface JavaScript

// Global variables
let currentPipelineId = null;
let currentPluginId = null;
let refreshInterval = null;

// API base URL
const API_BASE = '';

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize the application
function initializeApp() {
    // Load dashboard data if on dashboard page
    if (window.location.pathname === '/web' || window.location.pathname === '/web/') {
        loadDashboardData();
        startDashboardRefresh();
    }
    
    // Load pipelines if on pipelines page
    if (window.location.pathname === '/web/pipelines') {
        loadPipelines();
    }
    
    // Load plugins if on plugins page
    if (window.location.pathname === '/web/plugins') {
        loadPlugins();
    }
    
    // Load monitoring data if on monitoring page
    if (window.location.pathname === '/web/monitoring') {
        loadMonitoringData();
        startMonitoringRefresh();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Dashboard functions
function loadDashboardData() {
    Promise.all([
        fetch('/api/pipelines').then(r => r.ok ? r.json() : { pipelines: [] }),
        fetch('/api/plugins').then(r => r.ok ? r.json() : { plugins: [] }),
        fetch('/health').then(r => r.ok ? r.json() : { status: 'unknown' })
    ]).then(([pipelinesData, pluginsData, healthData]) => {
        updateDashboardStats(pipelinesData, pluginsData, healthData);
        loadRecentActivity();
    }).catch(error => {
        console.error('Error loading dashboard data:', error);
        showAlert('Error loading dashboard data', 'danger');
    });
}

function updateDashboardStats(pipelinesData, pluginsData, healthData) {
    const pipelineCount = pipelinesData.pipelines ? pipelinesData.pipelines.length : 0;
    const pluginCount = pluginsData.plugins ? pluginsData.plugins.length : 0;
    
    document.getElementById('pipeline-count').textContent = pipelineCount;
    document.getElementById('plugin-count').textContent = pluginCount;
    document.getElementById('active-jobs').textContent = '0'; // TODO: Implement active jobs counter
    document.getElementById('system-status').textContent = healthData.status || 'Unknown';
}

function loadRecentActivity() {
    const activityContainer = document.getElementById('recent-activity');
    if (!activityContainer) return;
    
    // Mock data for now - replace with actual API call
    const activities = [
        { time: '2 minutes ago', action: 'Pipeline "Data ETL" completed successfully', type: 'success' },
        { time: '5 minutes ago', action: 'Plugin "Oracle Connector" registered', type: 'info' },
        { time: '10 minutes ago', action: 'Pipeline "Log Processing" started', type: 'info' },
        { time: '15 minutes ago', action: 'System health check passed', type: 'success' }
    ];
    
    const html = activities.map(activity => `
        <div class="d-flex align-items-center mb-2">
            <div class="flex-shrink-0">
                <i class="fas fa-circle text-${activity.type === 'success' ? 'success' : 'info'} fa-xs"></i>
            </div>
            <div class="flex-grow-1 ms-2">
                <small class="text-muted">${activity.time}</small><br>
                <span>${activity.action}</span>
            </div>
        </div>
    `).join('');
    
    activityContainer.innerHTML = html;
}

function startDashboardRefresh() {
    refreshInterval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
}

// Pipeline functions
function loadPipelines() {
    const tableBody = document.getElementById('pipelinesTableBody');
    if (!tableBody) return;
    
    fetch('/api/pipelines')
        .then(response => response.ok ? response.json() : { pipelines: [] })
        .then(data => {
            const pipelines = data.pipelines || [];
            
            if (pipelines.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center text-muted">
                            <i class="fas fa-inbox"></i> No pipelines found
                        </td>
                    </tr>
                `;
                return;
            }
            
            const html = pipelines.map(pipeline => `
                <tr>
                    <td>${pipeline.id}</td>
                    <td><strong>${pipeline.name}</strong></td>
                    <td><span class="status-badge status-${pipeline.status}">${pipeline.status}</span></td>
                    <td>${pipeline.steps ? pipeline.steps.length : 0}</td>
                    <td>${formatDate(pipeline.created_at)}</td>
                    <td>${formatDate(pipeline.updated_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewPipeline(${pipeline.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="executePipeline(${pipeline.id})">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deletePipeline(${pipeline.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
            tableBody.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading pipelines:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle"></i> Error loading pipelines
                    </td>
                </tr>
            `;
        });
}

function createPipeline() {
    const modal = new bootstrap.Modal(document.getElementById('createPipelineModal'));
    modal.show();
}

function submitCreatePipeline() {
    const form = document.getElementById('createPipelineForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const formData = {
        name: document.getElementById('pipelineName').value,
        description: document.getElementById('pipelineDescription').value,
        type: document.getElementById('pipelineType').value
    };
    
    fetch('/api/pipelines', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
            return;
        }
        
        showAlert('Pipeline created successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('createPipelineModal')).hide();
        form.reset();
        loadPipelines();
    })
    .catch(error => {
        console.error('Error creating pipeline:', error);
        showAlert('Error creating pipeline', 'danger');
    });
}

function viewPipeline(id) {
    window.location.href = `/web/pipelines/${id}`;
}

function executePipeline(id) {
    if (!confirm('Are you sure you want to execute this pipeline?')) {
        return;
    }
    
    fetch(`/api/pipelines/${id}/execute`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
            return;
        }
        
        showAlert('Pipeline execution started', 'success');
        loadPipelines();
    })
    .catch(error => {
        console.error('Error executing pipeline:', error);
        showAlert('Error executing pipeline', 'danger');
    });
}

function deletePipeline(id) {
    if (!confirm('Are you sure you want to delete this pipeline? This action cannot be undone.')) {
        return;
    }
    
    fetch(`/api/pipelines/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            showAlert('Pipeline deleted successfully', 'success');
            loadPipelines();
        } else {
            showAlert('Error deleting pipeline', 'danger');
        }
    })
    .catch(error => {
        console.error('Error deleting pipeline:', error);
        showAlert('Error deleting pipeline', 'danger');
    });
}

function searchPipelines() {
    const query = document.getElementById('searchPipelines').value.toLowerCase();
    const rows = document.querySelectorAll('#pipelinesTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
    });
}

// Plugin functions
function loadPlugins() {
    const container = document.getElementById('pluginsGrid');
    if (!container) return;
    
    fetch('/api/plugins')
        .then(response => response.ok ? response.json() : { plugins: [] })
        .then(data => {
            const plugins = data.plugins || [];
            
            if (plugins.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center text-muted">
                        <i class="fas fa-inbox"></i> No plugins found
                    </div>
                `;
                return;
            }
            
            const html = plugins.map(plugin => `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="plugin-card" onclick="viewPlugin(${plugin.id})">
                        <div class="plugin-icon plugin-${plugin.type}">
                            <i class="fas fa-${getPluginIcon(plugin.type)}"></i>
                        </div>
                        <h6 class="fw-bold">${plugin.name}</h6>
                        <p class="text-muted small mb-2">${plugin.description || 'No description'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">v${plugin.version}</small>
                            <span class="status-badge status-${plugin.status}">${plugin.status}</span>
                        </div>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading plugins:', error);
            container.innerHTML = `
                <div class="col-12 text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i> Error loading plugins
                </div>
            `;
        });
}

function getPluginIcon(type) {
    const icons = {
        extractor: 'download',
        loader: 'upload',
        transformer: 'cogs',
        utility: 'tools'
    };
    return icons[type] || 'plug';
}

function registerPlugin() {
    const modal = new bootstrap.Modal(document.getElementById('registerPluginModal'));
    modal.show();
}

function submitRegisterPlugin() {
    const form = document.getElementById('registerPluginForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const formData = {
        name: document.getElementById('pluginName').value,
        version: document.getElementById('pluginVersion').value,
        type: document.getElementById('pluginType').value,
        description: document.getElementById('pluginDescription').value,
        config: document.getElementById('pluginConfig').value
    };
    
    // Validate JSON config
    if (formData.config) {
        try {
            JSON.parse(formData.config);
        } catch (e) {
            showAlert('Invalid JSON configuration', 'danger');
            return;
        }
    }
    
    fetch('/api/plugins', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
            return;
        }
        
        showAlert('Plugin registered successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('registerPluginModal')).hide();
        form.reset();
        loadPlugins();
    })
    .catch(error => {
        console.error('Error registering plugin:', error);
        showAlert('Error registering plugin', 'danger');
    });
}

function viewPlugin(id) {
    currentPluginId = id;
    // Load plugin details and show modal
    const modal = new bootstrap.Modal(document.getElementById('pluginDetailModal'));
    modal.show();
    // TODO: Load actual plugin details
}

function searchPlugins() {
    const query = document.getElementById('searchPlugins').value.toLowerCase();
    const cards = document.querySelectorAll('.plugin-card');
    
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.parentElement.style.display = text.includes(query) ? '' : 'none';
    });
}

// Monitoring functions
function loadMonitoringData() {
    Promise.all([
        fetch('/metrics').then(r => r.ok ? r.text() : ''),
        fetch('/health').then(r => r.ok ? r.json() : {})
    ]).then(([metricsText, healthData]) => {
        updateMonitoringStats(metricsText, healthData);
        updateSystemResourceCharts();
        loadSystemLogs();
    }).catch(error => {
        console.error('Error loading monitoring data:', error);
    });
}

function updateMonitoringStats(metricsText, healthData) {
    // Mock data - replace with actual metrics parsing
    document.getElementById('cpu-usage').textContent = Math.floor(Math.random() * 100) + '%';
    document.getElementById('memory-usage').textContent = Math.floor(Math.random() * 100) + '%';
    document.getElementById('active-connections').textContent = Math.floor(Math.random() * 50);
    document.getElementById('uptime').textContent = '2d 14h 32m';
    
    // Update progress bars
    const cpuPercent = Math.floor(Math.random() * 100);
    const memoryPercent = Math.floor(Math.random() * 100);
    const diskPercent = Math.floor(Math.random() * 100);
    const networkPercent = Math.floor(Math.random() * 100);
    
    document.getElementById('cpu-progress').style.width = cpuPercent + '%';
    document.getElementById('memory-progress').style.width = memoryPercent + '%';
    document.getElementById('disk-progress').style.width = diskPercent + '%';
    document.getElementById('network-progress').style.width = networkPercent + '%';
}

function updateSystemResourceCharts() {
    // TODO: Implement actual chart rendering with Chart.js or similar
    console.log('Updating system resource charts...');
}

function loadSystemLogs() {
    const logsTable = document.getElementById('logs-table');
    if (!logsTable) return;
    
    // Mock logs data
    const logs = [
        { timestamp: '2025-06-30 15:30:45', level: 'INFO', component: 'API', message: 'Server started successfully' },
        { timestamp: '2025-06-30 15:30:46', level: 'INFO', component: 'DB', message: 'Database connection established' },
        { timestamp: '2025-06-30 15:30:47', level: 'WARN', component: 'PLUGIN', message: 'Plugin initialization took longer than expected' },
        { timestamp: '2025-06-30 15:30:48', level: 'INFO', component: 'PIPELINE', message: 'Pipeline executor initialized' }
    ];
    
    const html = logs.map(log => `
        <tr>
            <td><small>${log.timestamp}</small></td>
            <td><span class="badge bg-${getLevelColor(log.level)}">${log.level}</span></td>
            <td><small>${log.component}</small></td>
            <td>${log.message}</td>
        </tr>
    `).join('');
    
    logsTable.innerHTML = html;
}

function getLevelColor(level) {
    const colors = {
        ERROR: 'danger',
        WARN: 'warning',
        INFO: 'info',
        DEBUG: 'secondary'
    };
    return colors[level] || 'secondary';
}

function startMonitoringRefresh() {
    refreshInterval = setInterval(loadMonitoringData, 15000); // Refresh every 15 seconds
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" id="${alertId}" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-remove alert after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// Quick action functions
function viewLogs() {
    window.location.href = '/web/monitoring';
}

function runDiagnostics() {
    showAlert('Running system diagnostics...', 'info');
    
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'healthy') {
                showAlert('System diagnostics passed', 'success');
            } else {
                showAlert('System diagnostics found issues', 'warning');
            }
        })
        .catch(error => {
            showAlert('Diagnostics failed', 'danger');
        });
}

// Cleanup when leaving page
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
