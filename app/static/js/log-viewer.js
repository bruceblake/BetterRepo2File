class LogViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.logBuffer = [];
        this.maxLogs = 1000;
        this.autoScroll = true;
        this.filters = {
            level: 'all',
            search: ''
        };
        
        this.init();
    }
    
    init() {
        this.createUI();
        this.setupEventHandlers();
        this.startLogStreaming();
    }
    
    createUI() {
        this.container.innerHTML = `
            <div class="log-viewer">
                <div class="log-controls">
                    <select id="logLevelFilter" class="log-filter">
                        <option value="all">All Levels</option>
                        <option value="DEBUG">Debug</option>
                        <option value="INFO">Info</option>
                        <option value="WARNING">Warning</option>
                        <option value="ERROR">Error</option>
                    </select>
                    
                    <input type="text" id="logSearch" class="log-search" 
                           placeholder="Search logs...">
                    
                    <button id="clearLogs" class="btn-clear">Clear</button>
                    
                    <label class="auto-scroll-label">
                        <input type="checkbox" id="autoScroll" checked>
                        Auto-scroll
                    </label>
                </div>
                
                <div class="log-content" id="logContent">
                    <div class="log-empty">No logs yet...</div>
                </div>
                
                <div class="log-stats">
                    <span id="logCount">0 logs</span>
                    <span id="errorCount">0 errors</span>
                    <span id="warningCount">0 warnings</span>
                </div>
            </div>
        `;
        
        this.logContent = document.getElementById('logContent');
    }
    
    setupEventHandlers() {
        document.getElementById('logLevelFilter').addEventListener('change', (e) => {
            this.filters.level = e.target.value;
            this.renderLogs();
        });
        
        document.getElementById('logSearch').addEventListener('input', (e) => {
            this.filters.search = e.target.value.toLowerCase();
            this.renderLogs();
        });
        
        document.getElementById('clearLogs').addEventListener('click', () => {
            this.clearLogs();
        });
        
        document.getElementById('autoScroll').addEventListener('change', (e) => {
            this.autoScroll = e.target.checked;
        });
    }
    
    startLogStreaming() {
        // Connect to server-sent events for real-time logs
        this.eventSource = new EventSource('/api/logs/stream');
        
        this.eventSource.onmessage = (event) => {
            const log = JSON.parse(event.data);
            this.addLog(log);
        };
        
        this.eventSource.onerror = (error) => {
            console.error('Log streaming error:', error);
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.startLogStreaming(), 5000);
        };
    }
    
    addLog(log) {
        // Add timestamp if not present
        if (!log.timestamp) {
            log.timestamp = new Date().toISOString();
        }
        
        this.logBuffer.push(log);
        
        // Limit buffer size
        if (this.logBuffer.length > this.maxLogs) {
            this.logBuffer.shift();
        }
        
        // Update stats
        this.updateStats();
        
        // Render if log passes filters
        if (this.shouldShowLog(log)) {
            this.appendLogEntry(log);
        }
    }
    
    shouldShowLog(log) {
        // Check level filter
        if (this.filters.level !== 'all' && log.level !== this.filters.level) {
            return false;
        }
        
        // Check search filter
        if (this.filters.search) {
            const searchText = `${log.message} ${log.details || ''}`.toLowerCase();
            if (!searchText.includes(this.filters.search)) {
                return false;
            }
        }
        
        return true;
    }
    
    appendLogEntry(log) {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${log.level.toLowerCase()}`;
        
        logEntry.innerHTML = `
            <span class="log-timestamp">${this.formatTimestamp(log.timestamp)}</span>
            <span class="log-level">${log.level}</span>
            <span class="log-message">${this.escapeHtml(log.message)}</span>
            ${log.details ? `<pre class="log-details">${this.escapeHtml(JSON.stringify(log.details, null, 2))}</pre>` : ''}
            ${log.source ? `<span class="log-source">${log.source}</span>` : ''}
        `;
        
        this.logContent.appendChild(logEntry);
        
        // Remove empty message
        const emptyMsg = this.logContent.querySelector('.log-empty');
        if (emptyMsg) {
            emptyMsg.remove();
        }
        
        // Auto-scroll if enabled
        if (this.autoScroll) {
            this.logContent.scrollTop = this.logContent.scrollHeight;
        }
    }
    
    renderLogs() {
        this.logContent.innerHTML = '';
        
        const filteredLogs = this.logBuffer.filter(log => this.shouldShowLog(log));
        
        if (filteredLogs.length === 0) {
            this.logContent.innerHTML = '<div class="log-empty">No logs match the current filters...</div>';
            return;
        }
        
        filteredLogs.forEach(log => this.appendLogEntry(log));
        
        if (this.autoScroll) {
            this.logContent.scrollTop = this.logContent.scrollHeight;
        }
    }
    
    clearLogs() {
        this.logBuffer = [];
        this.logContent.innerHTML = '<div class="log-empty">Logs cleared</div>';
        this.updateStats();
    }
    
    updateStats() {
        const stats = {
            total: this.logBuffer.length,
            errors: this.logBuffer.filter(log => log.level === 'ERROR').length,
            warnings: this.logBuffer.filter(log => log.level === 'WARNING').length
        };
        
        document.getElementById('logCount').textContent = `${stats.total} logs`;
        document.getElementById('errorCount').textContent = `${stats.errors} errors`;
        document.getElementById('warningCount').textContent = `${stats.warnings} warnings`;
    }
    
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3
        });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    destroy() {
        if (this.eventSource) {
            this.eventSource.close();
        }
    }
}

// CSS for the log viewer
const logViewerStyles = `
<style>
.log-viewer {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    overflow: hidden;
}

.log-controls {
    display: flex;
    gap: 10px;
    padding: 10px;
    background: white;
    border-bottom: 1px solid #dee2e6;
    align-items: center;
}

.log-filter, .log-search {
    padding: 6px 12px;
    border: 1px solid #dee2e6;
    border-radius: 4px;
}

.log-search {
    flex: 1;
    min-width: 200px;
}

.btn-clear {
    padding: 6px 12px;
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn-clear:hover {
    background: #c82333;
}

.auto-scroll-label {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 14px;
}

.log-content {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
}

.log-empty {
    text-align: center;
    color: #6c757d;
    padding: 20px;
    font-style: italic;
}

.log-entry {
    display: flex;
    gap: 10px;
    padding: 4px 8px;
    border-radius: 4px;
    margin-bottom: 2px;
    word-break: break-word;
}

.log-entry:hover {
    background: #f0f0f0;
}

.log-debug {
    color: #6c757d;
}

.log-info {
    color: #0d6efd;
}

.log-warning {
    color: #ffc107;
    background: #fffbee;
}

.log-error {
    color: #dc3545;
    background: #fff5f5;
}

.log-timestamp {
    color: #6c757d;
    white-space: nowrap;
}

.log-level {
    font-weight: bold;
    width: 70px;
}

.log-message {
    flex: 1;
}

.log-details {
    width: 100%;
    margin-top: 5px;
    padding: 5px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 12px;
    overflow-x: auto;
}

.log-source {
    color: #6c757d;
    font-style: italic;
    font-size: 11px;
}

.log-stats {
    display: flex;
    gap: 20px;
    padding: 10px;
    background: white;
    border-top: 1px solid #dee2e6;
    font-size: 14px;
}

.log-stats span {
    color: #6c757d;
}

#errorCount {
    color: #dc3545;
}

#warningCount {
    color: #ffc107;
}
</style>
`;

// Export for use in other modules
window.LogViewer = LogViewer;