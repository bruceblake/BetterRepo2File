class IterationDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.iterations = [];
        this.currentIteration = null;
        this.charts = {};
        
        this.init();
    }
    
    init() {
        this.createUI();
        this.setupEventHandlers();
        this.loadIterationHistory();
        this.startPolling();
    }
    
    createUI() {
        this.container.innerHTML = `
            <div class="iteration-dashboard">
                <div class="dashboard-header">
                    <h2>Iteration Dashboard</h2>
                    <button id="refreshDashboard" class="btn-refresh">
                        <span class="material-symbols-outlined">refresh</span>
                    </button>
                </div>
                
                <div class="current-iteration">
                    <h3>Current Iteration</h3>
                    <div id="currentIterationInfo" class="iteration-info">
                        <p class="no-iteration">No active iteration</p>
                    </div>
                </div>
                
                <div class="iteration-metrics">
                    <h3>Metrics</h3>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">Total Iterations</div>
                            <div class="metric-value" id="totalIterations">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Success Rate</div>
                            <div class="metric-value" id="successRate">0%</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Avg Duration</div>
                            <div class="metric-value" id="avgDuration">0s</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Total Errors</div>
                            <div class="metric-value" id="totalErrors">0</div>
                        </div>
                    </div>
                </div>
                
                <div class="iteration-charts">
                    <h3>Visualizations</h3>
                    <div class="charts-grid">
                        <div class="chart-container">
                            <canvas id="durationChart"></canvas>
                        </div>
                        <div class="chart-container">
                            <canvas id="successChart"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="iteration-history">
                    <h3>Iteration History</h3>
                    <div class="history-controls">
                        <input type="text" id="historySearch" placeholder="Search iterations...">
                        <select id="historyFilter">
                            <option value="all">All</option>
                            <option value="completed">Completed</option>
                            <option value="failed">Failed</option>
                            <option value="in_progress">In Progress</option>
                        </select>
                    </div>
                    <div id="iterationHistory" class="history-list">
                        <div class="history-empty">No iterations yet</div>
                    </div>
                </div>
                
                <div class="diff-viewer" id="diffViewer" style="display: none;">
                    <h3>Code Changes</h3>
                    <div id="diffContent"></div>
                </div>
            </div>
        `;
    }
    
    setupEventHandlers() {
        document.getElementById('refreshDashboard').addEventListener('click', () => {
            this.loadIterationHistory();
        });
        
        document.getElementById('historySearch').addEventListener('input', (e) => {
            this.filterHistory(e.target.value);
        });
        
        document.getElementById('historyFilter').addEventListener('change', (e) => {
            this.filterHistory(null, e.target.value);
        });
    }
    
    loadIterationHistory() {
        fetch('/api/iterations/history')
            .then(res => res.json())
            .then(data => {
                this.iterations = data.iterations || [];
                this.currentIteration = data.current_iteration;
                this.updateDashboard();
            })
            .catch(error => {
                console.error('Failed to load iteration history:', error);
            });
    }
    
    updateDashboard() {
        this.updateCurrentIteration();
        this.updateMetrics();
        this.updateCharts();
        this.updateHistory();
    }
    
    updateCurrentIteration() {
        const container = document.getElementById('currentIterationInfo');
        
        if (!this.currentIteration) {
            container.innerHTML = '<p class="no-iteration">No active iteration</p>';
            return;
        }
        
        const duration = this.currentIteration.end_time ? 
            (this.currentIteration.end_time - this.currentIteration.start_time).toFixed(2) :
            (Date.now() / 1000 - this.currentIteration.start_time).toFixed(2);
        
        container.innerHTML = `
            <div class="iteration-card current">
                <div class="iteration-header">
                    <span class="iteration-id">${this.currentIteration.id}</span>
                    <span class="iteration-status status-${this.currentIteration.status || 'in_progress'}">
                        ${this.currentIteration.status || 'In Progress'}
                    </span>
                </div>
                <div class="iteration-description">${this.currentIteration.description || 'No description'}</div>
                <div class="iteration-steps">
                    <h4>Steps (${this.currentIteration.steps.length})</h4>
                    ${this.renderSteps(this.currentIteration.steps)}
                </div>
                <div class="iteration-footer">
                    <span>Duration: ${duration}s</span>
                    <span>Errors: ${this.currentIteration.errors.length}</span>
                </div>
            </div>
        `;
    }
    
    renderSteps(steps) {
        if (!steps.length) return '<p class="no-steps">No steps recorded</p>';
        
        return `
            <ul class="step-list">
                ${steps.map(step => `
                    <li class="step-item">
                        <span class="step-time">${this.formatTime(step.timestamp)}</span>
                        <span class="step-name">${step.step}</span>
                        ${step.details ? `<pre class="step-details">${JSON.stringify(step.details, null, 2)}</pre>` : ''}
                    </li>
                `).join('')}
            </ul>
        `;
    }
    
    updateMetrics() {
        const total = this.iterations.length;
        const completed = this.iterations.filter(i => i.status === 'completed').length;
        const failed = this.iterations.filter(i => i.status === 'failed').length;
        const totalErrors = this.iterations.reduce((sum, i) => sum + (i.errors?.length || 0), 0);
        
        const durations = this.iterations
            .filter(i => i.duration)
            .map(i => i.duration);
        const avgDuration = durations.length ? 
            (durations.reduce((a, b) => a + b, 0) / durations.length).toFixed(2) : 0;
        
        const successRate = total ? ((completed / total) * 100).toFixed(1) : 0;
        
        document.getElementById('totalIterations').textContent = total;
        document.getElementById('successRate').textContent = `${successRate}%`;
        document.getElementById('avgDuration').textContent = `${avgDuration}s`;
        document.getElementById('totalErrors').textContent = totalErrors;
    }
    
    updateCharts() {
        // Duration trend chart
        const durationCtx = document.getElementById('durationChart').getContext('2d');
        if (this.charts.duration) this.charts.duration.destroy();
        
        const durationData = this.iterations
            .filter(i => i.duration)
            .slice(-20); // Last 20 iterations
        
        this.charts.duration = new Chart(durationCtx, {
            type: 'line',
            data: {
                labels: durationData.map(i => i.id.slice(0, 8)),
                datasets: [{
                    label: 'Duration (seconds)',
                    data: durationData.map(i => i.duration),
                    borderColor: 'rgb(75, 192, 192)',
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Iteration Duration Trend'
                    }
                }
            }
        });
        
        // Success rate pie chart
        const successCtx = document.getElementById('successChart').getContext('2d');
        if (this.charts.success) this.charts.success.destroy();
        
        const statusCounts = {
            completed: this.iterations.filter(i => i.status === 'completed').length,
            failed: this.iterations.filter(i => i.status === 'failed').length,
            in_progress: this.iterations.filter(i => i.status === 'in_progress').length
        };
        
        this.charts.success = new Chart(successCtx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'Failed', 'In Progress'],
                datasets: [{
                    data: [statusCounts.completed, statusCounts.failed, statusCounts.in_progress],
                    backgroundColor: [
                        'rgb(34, 197, 94)',
                        'rgb(239, 68, 68)',
                        'rgb(251, 191, 36)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Iteration Status Distribution'
                    }
                }
            }
        });
    }
    
    updateHistory() {
        const container = document.getElementById('iterationHistory');
        
        if (!this.iterations.length) {
            container.innerHTML = '<div class="history-empty">No iterations yet</div>';
            return;
        }
        
        const sortedIterations = [...this.iterations].reverse(); // Most recent first
        
        container.innerHTML = sortedIterations.map(iteration => `
            <div class="iteration-card" data-id="${iteration.id}">
                <div class="iteration-header">
                    <span class="iteration-id">${iteration.id.slice(0, 8)}</span>
                    <span class="iteration-status status-${iteration.status}">
                        ${iteration.status}
                    </span>
                </div>
                <div class="iteration-description">${iteration.description || 'No description'}</div>
                <div class="iteration-footer">
                    <span>Started: ${this.formatTime(iteration.start_time)}</span>
                    <span>Duration: ${iteration.duration ? iteration.duration.toFixed(2) + 's' : 'N/A'}</span>
                    <span>Steps: ${iteration.steps.length}</span>
                    <span>Errors: ${iteration.errors.length}</span>
                </div>
                <div class="iteration-actions">
                    <button class="btn-details" data-id="${iteration.id}">View Details</button>
                    <button class="btn-diff" data-id="${iteration.id}">View Changes</button>
                </div>
            </div>
        `).join('');
        
        // Add click handlers
        container.querySelectorAll('.btn-details').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.showIterationDetails(e.target.dataset.id);
            });
        });
        
        container.querySelectorAll('.btn-diff').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.showIterationDiff(e.target.dataset.id);
            });
        });
    }
    
    showIterationDetails(iterationId) {
        const iteration = this.iterations.find(i => i.id === iterationId);
        if (!iteration) return;
        
        // Show detailed modal with all information
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Iteration Details: ${iteration.id}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <h4>Description</h4>
                    <p>${iteration.description || 'No description'}</p>
                    
                    <h4>Steps</h4>
                    ${this.renderSteps(iteration.steps)}
                    
                    <h4>Errors</h4>
                    ${this.renderErrors(iteration.errors)}
                    
                    <h4>Metrics</h4>
                    ${this.renderMetrics(iteration.metrics)}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });
    }
    
    showIterationDiff(iterationId) {
        fetch(`/api/iterations/${iterationId}/diff`)
            .then(res => res.json())
            .then(diff => {
                const diffViewer = document.getElementById('diffViewer');
                const diffContent = document.getElementById('diffContent');
                
                diffContent.innerHTML = diff.html_diff || 'No changes available';
                diffViewer.style.display = 'block';
                
                // Scroll to diff viewer
                diffViewer.scrollIntoView({ behavior: 'smooth' });
            })
            .catch(error => {
                console.error('Failed to load diff:', error);
            });
    }
    
    renderErrors(errors) {
        if (!errors.length) return '<p>No errors</p>';
        
        return `
            <ul class="error-list">
                ${errors.map(error => `
                    <li class="error-item">
                        <span class="error-time">${this.formatTime(error.timestamp)}</span>
                        <span class="error-message">${error.error}</span>
                        ${error.exception ? `<pre class="error-trace">${error.traceback}</pre>` : ''}
                    </li>
                `).join('')}
            </ul>
        `;
    }
    
    renderMetrics(metrics) {
        if (!metrics || !Object.keys(metrics).length) return '<p>No metrics recorded</p>';
        
        return `
            <table class="metrics-table">
                ${Object.entries(metrics).map(([key, value]) => `
                    <tr>
                        <td>${key}</td>
                        <td>${typeof value === 'object' ? JSON.stringify(value, null, 2) : value}</td>
                    </tr>
                `).join('')}
            </table>
        `;
    }
    
    filterHistory(search, status) {
        // Implementation for filtering history items
        const container = document.getElementById('iterationHistory');
        const cards = container.querySelectorAll('.iteration-card');
        
        cards.forEach(card => {
            let show = true;
            
            if (search) {
                const text = card.textContent.toLowerCase();
                show = show && text.includes(search.toLowerCase());
            }
            
            if (status && status !== 'all') {
                const cardStatus = card.querySelector('.iteration-status').textContent.toLowerCase();
                show = show && cardStatus === status;
            }
            
            card.style.display = show ? 'block' : 'none';
        });
    }
    
    formatTime(timestamp) {
        if (!timestamp) return 'N/A';
        const date = new Date(timestamp * 1000);
        return date.toLocaleString();
    }
    
    startPolling() {
        // Poll for updates every 5 seconds
        setInterval(() => {
            if (this.currentIteration && this.currentIteration.status === 'in_progress') {
                this.loadIterationHistory();
            }
        }, 5000);
    }
}

// CSS for the dashboard
const dashboardStyles = `
<style>
.iteration-dashboard {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.btn-refresh {
    background: none;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 8px;
    cursor: pointer;
}

.btn-refresh:hover {
    background: #f8f9fa;
}

.current-iteration, .iteration-metrics, .iteration-charts, .iteration-history, .diff-viewer {
    margin-bottom: 30px;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.metric-card {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
}

.metric-label {
    font-size: 14px;
    color: #6c757d;
    margin-bottom: 5px;
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #212529;
}

.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

.chart-container {
    height: 300px;
}

.history-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.history-controls input, .history-controls select {
    padding: 8px 12px;
    border: 1px solid #dee2e6;
    border-radius: 4px;
}

.history-controls input {
    flex: 1;
}

.iteration-card {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
    background: #f8f9fa;
}

.iteration-card.current {
    background: #e3f2fd;
    border-color: #2196f3;
}

.iteration-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.iteration-id {
    font-weight: bold;
    font-family: monospace;
}

.iteration-status {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

.status-completed {
    background: #d4edda;
    color: #155724;
}

.status-failed {
    background: #f8d7da;
    color: #721c24;
}

.status-in_progress {
    background: #fff3cd;
    color: #856404;
}

.iteration-description {
    margin-bottom: 10px;
    color: #495057;
}

.iteration-footer {
    display: flex;
    gap: 20px;
    font-size: 14px;
    color: #6c757d;
}

.iteration-actions {
    margin-top: 10px;
    display: flex;
    gap: 10px;
}

.iteration-actions button {
    padding: 6px 12px;
    border: 1px solid #dee2e6;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.iteration-actions button:hover {
    background: #e9ecef;
}

.step-list {
    list-style: none;
    padding-left: 0;
}

.step-item {
    padding: 8px;
    border-left: 3px solid #dee2e6;
    margin-bottom: 5px;
    background: #f8f9fa;
}

.step-time {
    font-size: 12px;
    color: #6c757d;
    margin-right: 10px;
}

.step-details {
    margin-top: 5px;
    font-size: 12px;
    background: white;
    padding: 5px;
    border: 1px solid #dee2e6;
    border-radius: 4px;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    max-width: 800px;
    max-height: 80vh;
    overflow: auto;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #dee2e6;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6c757d;
}

.modal-body {
    padding: 20px;
}
</style>
`;

// Export for use
window.IterationDashboard = IterationDashboard;