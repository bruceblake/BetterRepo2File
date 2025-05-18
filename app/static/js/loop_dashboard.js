// Loop Dashboard JavaScript

class LoopDashboard {
    constructor() {
        this.sessionId = null;
        this.currentPhase = 'initialize';
        this.pollingInterval = null;
        this.logEntries = [];
        
        this.initializeUI();
        this.loadSessionFromUrl();
        this.attachEventListeners();
    }
    
    initializeUI() {
        // Get DOM elements
        this.elements = {
            sessionId: document.getElementById('sessionId'),
            featureVibe: document.getElementById('featureVibe'),
            repoPath: document.getElementById('repoPath'),
            iterationNumber: document.getElementById('iterationNumber'),
            
            // Phase indicators
            phases: document.querySelectorAll('.phase'),
            
            // Action buttons
            startLoopBtn: document.getElementById('startLoopBtn'),
            generateSectionABtn: document.getElementById('generateSectionABtn'),
            analyzeChangesBtn: document.getElementById('analyzeChangesBtn'),
            generateSectionCBtn: document.getElementById('generateSectionCBtn'),
            viewHistoryBtn: document.getElementById('viewHistoryBtn'),
            
            // Content areas
            sectionAContent: document.getElementById('sectionAContent'),
            sectionBContent: document.getElementById('sectionBContent'),
            sectionCContent: document.getElementById('sectionCContent'),
            commitList: document.getElementById('commitList'),
            testsPassed: document.getElementById('testsPassed'),
            testsFailed: document.getElementById('testsFailed'),
            testsErrors: document.getElementById('testsErrors'),
            testDetails: document.getElementById('testDetails'),
            logEntries: document.getElementById('logEntries'),
            
            // Section actions
            copySectionABtn: document.getElementById('copySectionABtn'),
            editSectionABtn: document.getElementById('editSectionABtn'),
            copySectionBBtn: document.getElementById('copySectionBBtn'),
            editSectionBBtn: document.getElementById('editSectionBBtn'),
            copySectionCBtn: document.getElementById('copySectionCBtn'),
            saveSectionCBtn: document.getElementById('saveSectionCBtn'),
            
            // Quick actions
            refreshStatusBtn: document.getElementById('refreshStatusBtn'),
            exportSessionBtn: document.getElementById('exportSessionBtn'),
            viewLogsBtn: document.getElementById('viewLogsBtn'),
            
            // Back button
            backToMain: document.getElementById('backToMain')
        };
    }
    
    attachEventListeners() {
        // Action buttons
        this.elements.startLoopBtn.addEventListener('click', () => this.startNewLoop());
        this.elements.generateSectionABtn.addEventListener('click', () => this.generateSectionA());
        this.elements.analyzeChangesBtn.addEventListener('click', () => this.analyzeChanges());
        this.elements.generateSectionCBtn.addEventListener('click', () => this.generateSectionC());
        this.elements.viewHistoryBtn.addEventListener('click', () => this.viewHistory());
        
        // Section actions
        this.elements.copySectionABtn.addEventListener('click', () => this.copyToClipboard('sectionAContent'));
        this.elements.editSectionABtn.addEventListener('click', () => this.editSection('sectionADisplay'));
        this.elements.copySectionBBtn.addEventListener('click', () => this.copyToClipboard('sectionBContent'));
        this.elements.editSectionBBtn.addEventListener('click', () => this.editSection('sectionBDisplay'));
        this.elements.copySectionCBtn.addEventListener('click', () => this.copyToClipboard('sectionCContent'));
        this.elements.saveSectionCBtn.addEventListener('click', () => this.saveSectionC());
        
        // Quick actions
        this.elements.refreshStatusBtn.addEventListener('click', () => this.refreshStatus());
        this.elements.exportSessionBtn.addEventListener('click', () => this.exportSession());
        this.elements.viewLogsBtn.addEventListener('click', () => this.viewLogs());
        
        // Back button
        this.elements.backToMain.addEventListener('click', () => {
            window.location.href = '/';
        });
    }
    
    loadSessionFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        this.sessionId = urlParams.get('session');
        
        if (!this.sessionId) {
            this.addLogEntry('error', 'No session ID provided in URL');
            return;
        }
        
        this.elements.sessionId.textContent = this.sessionId;
        this.loadSessionData();
        this.startPolling();
    }
    
    async loadSessionData() {
        try {
            const response = await fetch(`/api/v1/loop/status/${this.sessionId}`);
            if (!response.ok) {
                throw new Error('Failed to load session data');
            }
            
            const data = await response.json();
            this.updateUI(data);
            
        } catch (error) {
            this.addLogEntry('error', `Failed to load session: ${error.message}`);
        }
    }
    
    updateUI(sessionData) {
        // Update session info
        this.elements.featureVibe.textContent = sessionData.feature_vibe || 'Not set';
        this.elements.repoPath.textContent = sessionData.repo_path || 'Not set';
        this.elements.iterationNumber.textContent = sessionData.iterations?.length || '0';
        
        // Update phase indicator
        this.updatePhaseIndicator(sessionData.current_phase);
        
        // Update buttons based on phase
        this.updateButtonStates(sessionData.current_phase);
        
        // Update content sections
        if (sessionData.last_section_a) {
            this.elements.sectionAContent.textContent = sessionData.last_section_a;
        }
        
        if (sessionData.last_section_b) {
            this.elements.sectionBContent.textContent = sessionData.last_section_b;
        }
        
        if (sessionData.iterations?.length > 0) {
            const lastIteration = sessionData.iterations[sessionData.iterations.length - 1];
            if (lastIteration.section_c_content) {
                this.elements.sectionCContent.textContent = lastIteration.section_c_content;
            }
            
            // Update test results
            if (lastIteration.test_results) {
                this.updateTestResults(lastIteration.test_results);
            }
        }
        
        // Update commit history
        if (sessionData.commit_history) {
            this.updateCommitHistory(sessionData.commit_history);
        }
    }
    
    updatePhaseIndicator(currentPhase) {
        const phaseMap = {
            'initialized': 'initialize',
            'planning': 'planning',
            'coding': 'coding',
            'analyzing_changes': 'analyze',
            'diff_analysis_complete': 'analyze',
            'section_c_generated': 'brief',
            'completed': 'brief'
        };
        
        const mappedPhase = phaseMap[currentPhase] || 'initialize';
        
        // Reset all phases
        this.elements.phases.forEach(phase => {
            phase.classList.remove('active', 'completed', 'error');
        });
        
        // Mark completed and active phases
        let foundActive = false;
        this.elements.phases.forEach(phase => {
            const phaseName = phase.dataset.phase;
            if (phaseName === mappedPhase) {
                phase.classList.add('active');
                foundActive = true;
            } else if (!foundActive) {
                phase.classList.add('completed');
            }
        });
    }
    
    updateButtonStates(currentPhase) {
        // Reset all buttons
        const buttons = [
            this.elements.startLoopBtn,
            this.elements.generateSectionABtn,
            this.elements.analyzeChangesBtn,
            this.elements.generateSectionCBtn
        ];
        
        buttons.forEach(btn => btn.disabled = true);
        
        // Enable buttons based on phase
        switch(currentPhase) {
            case 'initialized':
                this.elements.generateSectionABtn.disabled = false;
                break;
            case 'planning':
                // Waiting for user to plan
                break;
            case 'coding':
                this.elements.analyzeChangesBtn.disabled = false;
                break;
            case 'diff_analysis_complete':
                this.elements.generateSectionCBtn.disabled = false;
                break;
            case 'section_c_generated':
            case 'completed':
                this.elements.startLoopBtn.disabled = false;
                break;
        }
    }
    
    updateTestResults(testResults) {
        this.elements.testsPassed.textContent = testResults.passed || 0;
        this.elements.testsFailed.textContent = testResults.failed || 0;
        this.elements.testsErrors.textContent = testResults.errors || 0;
        
        // Update details
        this.elements.testDetails.innerHTML = '';
        if (testResults.failure_details && testResults.failure_details.length > 0) {
            testResults.failure_details.forEach(failure => {
                const div = document.createElement('div');
                div.className = 'test-failure';
                div.textContent = failure;
                this.elements.testDetails.appendChild(div);
            });
        } else {
            this.elements.testDetails.innerHTML = '<div class="empty-state">No test failures</div>';
        }
    }
    
    updateCommitHistory(commits) {
        this.elements.commitList.innerHTML = '';
        
        if (!commits || commits.length === 0) {
            this.elements.commitList.innerHTML = '<div class="empty-state">No commits yet</div>';
            return;
        }
        
        commits.forEach(commit => {
            const div = document.createElement('div');
            div.className = 'commit-item';
            div.innerHTML = `
                <div class="commit-sha">${commit.sha.substring(0, 7)}</div>
                <div class="commit-message">${commit.message}</div>
                <div class="commit-tests">
                    Tests: ${commit.tests_passed ? '✅ Passed' : '❌ Failed'}
                    ${commit.test_summary ? ` - ${commit.test_summary}` : ''}
                </div>
            `;
            this.elements.commitList.appendChild(div);
        });
    }
    
    async generateSectionA() {
        try {
            this.addLogEntry('info', 'Generating Section A...');
            const response = await fetch(`/api/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    generate_section_a: true
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate Section A');
            }
            
            const data = await response.json();
            this.addLogEntry('success', 'Section A generated successfully');
            this.loadSessionData();
            
        } catch (error) {
            this.addLogEntry('error', `Failed to generate Section A: ${error.message}`);
        }
    }
    
    async analyzeChanges() {
        try {
            this.addLogEntry('info', 'Analyzing repository changes...');
            const response = await fetch(`/api/v1/loop/analyze_changes/${this.sessionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error('Failed to analyze changes');
            }
            
            const data = await response.json();
            this.addLogEntry('success', `Analysis complete - Iteration ${data.iteration}`);
            this.loadSessionData();
            
        } catch (error) {
            this.addLogEntry('error', `Failed to analyze changes: ${error.message}`);
        }
    }
    
    async generateSectionC() {
        try {
            this.addLogEntry('info', 'Generating Section C (Iteration Brief)...');
            const response = await fetch(`/api/v1/loop/generate_section_c/${this.sessionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate Section C');
            }
            
            const data = await response.json();
            this.addLogEntry('success', 'Section C generated successfully');
            this.loadSessionData();
            
        } catch (error) {
            this.addLogEntry('error', `Failed to generate Section C: ${error.message}`);
        }
    }
    
    async startNewLoop() {
        try {
            this.addLogEntry('info', 'Starting new loop iteration...');
            // Reset to planning phase
            this.updatePhaseIndicator('planning');
            this.updateButtonStates('planning');
            
        } catch (error) {
            this.addLogEntry('error', `Failed to start new loop: ${error.message}`);
        }
    }
    
    copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        const text = element.textContent;
        
        navigator.clipboard.writeText(text).then(() => {
            this.addLogEntry('success', 'Copied to clipboard');
        }).catch(err => {
            this.addLogEntry('error', 'Failed to copy to clipboard');
        });
    }
    
    editSection(sectionId) {
        const section = document.getElementById(sectionId);
        const content = section.querySelector('.section-content pre');
        
        if (section.classList.contains('editing')) {
            // Save changes
            const textarea = section.querySelector('textarea');
            content.textContent = textarea.value;
            textarea.remove();
            section.classList.remove('editing');
        } else {
            // Enter edit mode
            section.classList.add('editing');
            const textarea = document.createElement('textarea');
            textarea.value = content.textContent;
            section.querySelector('.section-content').appendChild(textarea);
            textarea.focus();
        }
    }
    
    async saveSectionC() {
        // TODO: Implement save functionality
        this.addLogEntry('info', 'Save functionality coming soon');
    }
    
    async refreshStatus() {
        this.addLogEntry('info', 'Refreshing status...');
        await this.loadSessionData();
        this.addLogEntry('success', 'Status refreshed');
    }
    
    async exportSession() {
        try {
            this.addLogEntry('info', 'Exporting session data...');
            const response = await fetch(`/api/v1/loop/export/${this.sessionId}`);
            
            if (!response.ok) {
                throw new Error('Failed to export session');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session_${this.sessionId}.json`;
            a.click();
            
            this.addLogEntry('success', 'Session exported successfully');
            
        } catch (error) {
            this.addLogEntry('error', `Failed to export session: ${error.message}`);
        }
    }
    
    viewHistory() {
        // Scroll to commit history
        this.elements.commitList.scrollIntoView({ behavior: 'smooth' });
    }
    
    viewLogs() {
        // Scroll to log entries
        this.elements.logEntries.scrollIntoView({ behavior: 'smooth' });
    }
    
    addLogEntry(type, message) {
        const timestamp = new Date().toLocaleTimeString();
        const entry = {
            type,
            message,
            timestamp
        };
        
        this.logEntries.push(entry);
        
        // Create DOM element
        const div = document.createElement('div');
        div.className = `log-entry ${type}`;
        div.innerHTML = `<span class="timestamp">${timestamp}</span>${message}`;
        
        this.elements.logEntries.appendChild(div);
        
        // Keep only last 50 entries
        if (this.logEntries.length > 50) {
            this.logEntries.shift();
            this.elements.logEntries.removeChild(this.elements.logEntries.firstChild);
        }
        
        // Scroll to bottom
        this.elements.logEntries.scrollTop = this.elements.logEntries.scrollHeight;
    }
    
    startPolling() {
        // Poll for updates every 5 seconds
        this.pollingInterval = setInterval(() => {
            this.loadSessionData();
        }, 5000);
    }
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.loopDashboard = new LoopDashboard();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.loopDashboard) {
        window.loopDashboard.stopPolling();
    }
});