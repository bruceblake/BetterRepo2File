// BetterRepo2File - Enhanced Workflow Controller
class WorkflowController {
    constructor() {
        this.state = {
            repoUrl: '',
            branch: 'main',
            vibe: '',
            plannerOutput: '',
            currentStep: 1,
            jobId: null,
            sessionId: null,
            lastCommitSha: null
        };
        
        this.init();
    }
    
    init() {
        this.attachEventListeners();
        this.cleanupOldData();
        this.loadSavedState();
        this.updateProgressIndicator();
        this.showStep(this.state.currentStep); // Make sure the current step is visible
    }
    
    cleanupOldData() {
        try {
            // Check localStorage size and clean if necessary
            let totalSize = 0;
            for (let key in localStorage) {
                if (localStorage.hasOwnProperty(key)) {
                    totalSize += localStorage[key].length + key.length;
                }
            }
            
            console.log('Current localStorage size:', (totalSize / 1024 / 1024).toFixed(2), 'MB');
            
            // If over 4MB (localStorage limit is usually 5MB)
            if (totalSize > 4 * 1024 * 1024) {
                console.log('Cleaning up localStorage...');
                this.clearOldStorageData();
                // Check size again after cleanup
                totalSize = 0;
                for (let key in localStorage) {
                    if (localStorage.hasOwnProperty(key)) {
                        totalSize += localStorage[key].length + key.length;
                    }
                }
                console.log('Size after cleanup:', (totalSize / 1024 / 1024).toFixed(2), 'MB');
            }
        } catch (e) {
            console.error('Error checking storage size:', e);
        }
    }
    
    attachEventListeners() {
        // Step buttons
        const generateBtn = document.getElementById('generateContextBtn');
        if (generateBtn) {
            console.log('Attaching generate context listener');
            generateBtn.addEventListener('click', () => {
                console.log('Generate context button clicked');
                this.generateContext();
            });
        } else {
            console.error('Generate context button not found');
        }
        
        document.getElementById('generateCoderContextBtn')?.addEventListener('click', () => this.generateCoderContext());
        document.getElementById('generateIterationBtn')?.addEventListener('click', () => this.generateIteration());
        document.getElementById('refinePromptBtn')?.addEventListener('click', () => this.refinePrompt());
        document.getElementById('generateCoderContextIterationBtn')?.addEventListener('click', () => this.generateIterationCoderContext());
        
        // Input listeners
        document.getElementById('githubUrlInputRepo')?.addEventListener('input', (e) => {
            this.state.repoUrl = e.target.value;
            this.saveState();
        });
        
        document.getElementById('githubBranch')?.addEventListener('input', (e) => {
            this.state.branch = e.target.value;
            this.saveState();
        });
        
        document.getElementById('vibeStatement')?.addEventListener('input', (e) => {
            this.state.vibe = e.target.value;
            this.saveState();
        });
        
        // Don't save large planner output to state
        document.getElementById('plannerOutput')?.addEventListener('input', (e) => {
            // Just keep it in the textarea, don't save to state to avoid quota issues
        });
    }
    
    saveState() {
        try {
            // Create a minimal state object to save space
            const minimalState = {
                repoUrl: this.state.repoUrl,
                branch: this.state.branch,
                vibe: this.state.vibe?.substring(0, 1000),  // Limit vibe to 1000 chars
                currentStep: this.state.currentStep,
                sessionId: this.state.sessionId,
                refinedVibe: this.state.refinedVibe?.substring(0, 1000),  // Limit refined vibe
                // Don't save large outputs or job data
            };
            
            localStorage.setItem('workflowState', JSON.stringify(minimalState));
        } catch (e) {
            if (e.name === 'QuotaExceededError') {
                console.warn('localStorage quota exceeded, clearing old data');
                // Clear old data and try again
                this.clearOldStorageData();
                try {
                    const essentialState = {
                        repoUrl: this.state.repoUrl,
                        branch: this.state.branch,
                        currentStep: this.state.currentStep,
                        sessionId: this.state.sessionId
                    };
                    localStorage.setItem('workflowState', JSON.stringify(essentialState));
                } catch (e2) {
                    console.error('Failed to save state even after cleanup:', e2);
                }
            } else {
                console.error('Error saving state:', e);
            }
        }
    }
    
    clearOldStorageData() {
        // Clear items that might be taking up space
        const keysToCheck = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('workflow') && key !== 'workflowState') {
                keysToCheck.push(key);
            }
        }
        
        // Remove old workflow data
        keysToCheck.forEach(key => {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.error('Error removing key:', key, e);
            }
        });
    }
    
    loadSavedState() {
        try {
            const saved = localStorage.getItem('workflowState');
            if (saved) {
                const savedState = JSON.parse(saved);
                // Only restore essential fields to avoid memory issues
                this.state.repoUrl = savedState.repoUrl || '';
                this.state.branch = savedState.branch || 'main';
                this.state.vibe = savedState.vibe || '';
                this.state.currentStep = savedState.currentStep || 1;
                this.state.sessionId = savedState.sessionId || null;
                this.state.refinedVibe = savedState.refinedVibe || '';
                
                this.restoreInputs();
            }
        } catch (e) {
            console.error('Error loading saved state:', e);
            // If there's an error, clear the corrupted data
            try {
                localStorage.removeItem('workflowState');
            } catch (e2) {
                console.error('Error clearing corrupted state:', e2);
            }
        }
    }
    
    restoreInputs() {
        const elements = {
            'githubUrlInputRepo': this.state.repoUrl,
            'githubBranch': this.state.branch,
            'vibeStatement': this.state.vibe,
            'plannerOutput': this.state.plannerOutput
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.value = value || '';
        });
    }
    
    updateProgressIndicator() {
        document.querySelectorAll('.progress-step').forEach((step, index) => {
            if (index + 1 <= this.state.currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }
    
    showStep(stepNumber) {
        document.querySelectorAll('.step-card').forEach(card => {
            card.classList.add('hidden');
        });
        
        let stepId;
        switch(stepNumber) {
            case 1: stepId = 'step1'; break;
            case 2: stepId = 'step2'; break;
            case 3: stepId = 'step3'; break;
            case 4: stepId = 'step4'; break;
            case 5: stepId = 'stepIteration'; break;
            case 6: stepId = 'stepIterationPlanning'; break;
            case 7: stepId = 'stepIterationCoding'; break;
            case 8: stepId = 'stepIterationCoding'; break;
            default: stepId = `step${stepNumber}`;
        }
        
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.remove('hidden');
        }
        
        this.state.currentStep = stepNumber;
        this.updateProgressIndicator();
        this.saveState();
    }
    
    showProgress(message, title = 'Processing...', step = null) {
        const overlay = document.getElementById('progressOverlay');
        const msgElement = document.getElementById('progressMessage');
        const titleElement = document.getElementById('progressTitle');
        const progressIcon = document.getElementById('progressIcon');
        
        if (overlay) {
            // Update main message and title
            if (msgElement) msgElement.textContent = message;
            if (titleElement) titleElement.textContent = title;
            
            // Update icon based on step
            if (progressIcon) {
                const icons = {
                    1: 'cloud_download',
                    2: 'analytics',
                    3: 'psychology',
                    4: 'description',
                    'clone': 'cloud_download',
                    'analyze': 'analytics',
                    'generate': 'psychology',
                    'finalize': 'description',
                    'error': 'error',
                    'success': 'check_circle'
                };
                progressIcon.textContent = icons[step] || 'hourglass_top';
                
                // Add animation classes for success/error
                progressIcon.className = 'material-symbols-outlined progress-icon-symbol';
                if (step === 'success') {
                    progressIcon.classList.add('success');
                } else if (step === 'error') {
                    progressIcon.classList.add('error');
                }
            }
            
            // Update progress steps
            const steps = document.querySelectorAll('.progress-step');
            steps.forEach((stepEl, index) => {
                if (step && typeof step === 'number') {
                    if (index + 1 < step) {
                        stepEl.classList.add('completed');
                        stepEl.classList.remove('active');
                    } else if (index + 1 === step) {
                        stepEl.classList.add('active');
                        stepEl.classList.remove('completed');
                    } else {
                        stepEl.classList.remove('active', 'completed');
                    }
                }
            });
            
            overlay.classList.remove('hidden');
        }
    }
    
    updateProgressBar(percent) {
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }
    }
    
    addProgressDetail(type, text) {
        const detailItem = document.getElementById(`${type}Detail`);
        if (detailItem) {
            detailItem.classList.remove('hidden');
            const textEl = detailItem.querySelector('.detail-text');
            if (textEl) textEl.textContent = text;
        }
    }
    
    hideProgress() {
        const overlay = document.getElementById('progressOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    async generateContext() {
        console.log('Generate context clicked');
        console.log('State:', this.state);
        
        if (!this.state.repoUrl || !this.state.vibe) {
            alert('Please provide both GitHub URL and feature description');
            return;
        }
        
        this.showProgress('Cloning repository from GitHub...', 'Repository Setup', 1);
        this.updateProgressBar(0);
        this.addProgressDetail('repo', this.state.repoUrl.split('/').slice(-1)[0]);
        
        try {
            console.log('Sending request to /api/generate_context');
            const response = await fetch('/api/generate_context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_url: this.state.repoUrl,
                    repo_branch: this.state.branch,
                    vibe: this.state.vibe,
                    stage: 'A'
                })
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Result:', result);
            
            if (result.success) {
                this.state.jobId = result.job_id;
                this.state.sessionId = result.session_id;
                await this.pollJob();
            } else {
                throw new Error(result.error || 'Failed to generate context');
            }
        } catch (error) {
            console.error('Error in generateContext:', error);
            alert('Error: ' + error.message);
            this.hideProgress();
        }
    }
    
    async generateCoderContext() {
        const plannerOutput = document.getElementById('plannerOutput').value;
        if (!plannerOutput) {
            alert('Please paste the AI planner output first');
            return;
        }
        
        this.showProgress('Processing AI planner output...', 'Context Generation', 2);
        this.updateProgressBar(30);
        
        try {
            const response = await fetch('/api/generate_context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_url: this.state.repoUrl,
                    repo_branch: this.state.branch,
                    vibe: this.state.vibe,
                    stage: 'B',
                    planner_output: plannerOutput
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.state.jobId = result.job_id;
                await this.pollJob();
            } else {
                throw new Error(result.error || 'Failed to generate context');
            }
        } catch (error) {
            alert('Error: ' + error.message);
            this.hideProgress();
        }
    }
    
    async generateIteration() {
        const feedbackText = document.getElementById('feedbackText').value;
        if (!feedbackText) {
            alert('Please provide feedback or issues');
            return;
        }
        
        // Store feedback for later use
        this.state.feedbackText = feedbackText;
        
        this.showProgress('Analyzing feedback and generating update context...', 'Iteration Planning', 3);
        this.updateProgressBar(60);
        
        try {
            // First, generate context for Gemini to re-plan based on feedback
            const response = await fetch('/api/generate_context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_url: this.state.repoUrl,
                    repo_branch: this.state.branch,
                    vibe: this.state.vibe,
                    stage: 'C',  // Stage C for iteration
                    feedback_log: feedbackText,
                    previous_planner_output: document.getElementById('plannerOutput')?.value || '',
                    session_id: this.state.sessionId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.state.jobId = result.job_id;
                await this.pollJob();
            } else {
                throw new Error(result.error || 'Failed to generate iteration');
            }
        } catch (error) {
            alert('Error: ' + error.message);
            this.hideProgress();
        }
    }
    
    async pollJob() {
        if (!this.state.jobId) return;
        
        const eventSource = new EventSource(`/api/job_status/${this.state.jobId}`);
        let progressPercent = 0;
        const progressMap = {
            'extracting': { step: 1, percent: 10, message: 'Cloning repository and extracting files...' },
            'analyzing': { step: 2, percent: 40, message: 'Analyzing code structure and patterns...' },
            'processing': { step: 3, percent: 70, message: 'AI is processing your request...' },
            'finalizing': { step: 4, percent: 90, message: 'Generating final output...' }
        };
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.phase) {
                const progress = progressMap[data.phase.toLowerCase()] || {};
                const step = progress.step || null;
                const percent = progress.percent || progressPercent;
                const message = progress.message || data.phase.charAt(0).toUpperCase() + data.phase.slice(1) + '...';
                
                // Update progress display
                if (step) {
                    this.showProgress(message, null, step);
                } else {
                    this.showProgress(message);
                }
                
                // Animate progress bar
                if (percent > progressPercent) {
                    progressPercent = percent;
                    this.updateProgressBar(percent);
                }
                
                // Add progress details
                if (data.current && data.total) {
                    this.addProgressDetail('files', `Processing ${data.current} of ${data.total} files`);
                }
            }
            
            if (data.status === 'completed') {
                eventSource.close();
                this.updateProgressBar(100);
                this.showProgress('Processing complete!', 'Success', 'success');
                setTimeout(() => {
                    this.displayResults(data.result);
                    this.hideProgress();
                }, 1000);
            } else if (data.error) {
                eventSource.close();
                this.showProgress('An error occurred: ' + data.error, 'Error', 'error');
                setTimeout(() => {
                    alert('Error: ' + data.error);
                    this.hideProgress();
                }, 2000);
            }
        };
        
        eventSource.onerror = () => {
            eventSource.close();
            alert('Connection lost. Please try again.');
            this.hideProgress();
        };
    }
    
    displayResults(result) {
        if (this.state.currentStep === 1) {
            // Show Section A output for initial planning
            const output = document.getElementById('sectionAOutput');
            if (output) {
                output.textContent = result.copy_text || 'No content generated';
            }
            this.showStep(2);
        } else if (this.state.currentStep === 3) {
            // Show Section B output for initial coding
            const output = document.getElementById('sectionBOutput');
            if (output) {
                output.textContent = result.copy_text || 'No content generated';
            }
            this.showStep(4);
        } else if (this.state.currentStep === 5) {
            // Show iteration output for Gemini re-planning
            const output = document.getElementById('iterationPlannerOutput');
            if (output) {
                output.textContent = result.copy_text || 'No content generated';
            }
            this.showStep(6);  // Go to iteration planning step
            
            // Show recent diff if available
            if (result.diff) {
                this.displayDiff(result.diff);
            }
        } else if (this.state.currentStep === 7) {
            // Show iteration coding output for Claude
            const output = document.getElementById('iterationCoderOutput');
            if (output) {
                output.textContent = result.copy_text || 'No content generated';
            }
            this.showStep(8);  // Go to iteration coding step
        }
    }
    
    async generateIterationCoderContext() {
        const iterationPlannerInput = document.getElementById('iterationPlannerInput').value;
        if (!iterationPlannerInput) {
            alert('Please paste Gemini\'s updated planning output first');
            return;
        }
        
        // Don't store large output in state
        this.showProgress('Generating implementation context for Claude...');
        
        try {
            const response = await fetch('/api/generate_context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_url: this.state.repoUrl,
                    repo_branch: this.state.branch,
                    vibe: this.state.vibe,
                    stage: 'D',  // New stage for iteration coding
                    planner_output: iterationPlannerInput,
                    feedback_log: this.state.feedbackText,
                    original_planner_output: this.state.plannerOutput
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.state.jobId = result.job_id;
                await this.pollJob();
            } else {
                throw new Error(result.error || 'Failed to generate context');
            }
        } catch (error) {
            alert('Error: ' + error.message);
            this.hideProgress();
        }
    }
    
    displayDiff(diff) {
        const diffView = document.getElementById('recentDiff');
        if (diffView) {
            diffView.innerHTML = `
                <div class="diff-stats">
                    <span class="additions">+${diff.additions || 0} additions</span>
                    <span class="deletions">-${diff.deletions || 0} deletions</span>
                    <span class="files">${diff.files?.length || 0} files changed</span>
                </div>
                <pre class="diff-content">${diff.content || ''}</pre>
            `;
        }
    }
    
    async refinePrompt() {
        const vibeInput = document.getElementById('vibeStatement');
        const refineBtn = document.getElementById('refinePromptBtn');
        
        if (!vibeInput.value.trim()) {
            alert('Please enter a feature description first');
            return;
        }
        
        // Disable button and show loading state
        refineBtn.disabled = true;
        refineBtn.innerHTML = '<span class="material-symbols-outlined">pending</span> Refining...';
        
        try {
            const response = await fetch('/api/refine_prompt_v2', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: vibeInput.value,
                    repo_url: this.state.repoUrl
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Show refined prompt section
                const refinedSection = document.getElementById('refinedPromptSection');
                const refinedText = document.getElementById('refinedPromptText');
                
                refinedSection.classList.remove('hidden');
                refinedText.textContent = result.refined_prompt;
                
                // Store the refined prompt
                this.state.refinedVibe = result.refined_prompt;
                this.saveState();
            } else {
                throw new Error(result.error || 'Failed to refine prompt');
            }
        } catch (error) {
            alert('Error refining prompt: ' + error.message);
        } finally {
            // Restore button state
            refineBtn.disabled = false;
            refineBtn.innerHTML = '<span class="material-symbols-outlined">auto_awesome</span> Refine with AI';
        }
    }
}

// Test Runner Functions
async function checkDockerAvailable() {
    try {
        const response = await fetch('/api/check-docker');
        const data = await response.json();
        return data.can_use_docker || false;
    } catch (error) {
        console.error('Error checking Docker availability:', error);
        return false;
    }
}

async function runTests() {
    const testBtn = event.target;
    testBtn.disabled = true;
    testBtn.innerHTML = '<span class="material-symbols-outlined">pending</span> Running...';
    
    try {
        // Always try to use Docker if available
        let useDocker = true; // Default to true for WSL/Docker environments
        
        console.log('Running tests with:', {
            repo_path: window.workflow.state.repoUrl,
            session_id: window.workflow.state.sessionId,
            use_docker: useDocker
        });
        
        const response = await fetch('/api/run-tests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                repo_path: window.workflow.state.repoUrl,
                session_id: window.workflow.state.sessionId,
                use_docker: useDocker,
                framework: 'auto'  // Let backend auto-detect
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Test result:', result);
        displayTestResults(result.results || result);
        
    } catch (error) {
        console.error('Error running tests:', error);
        displayTestResults({ error: error.message });
    } finally {
        testBtn.disabled = false;
        testBtn.innerHTML = '<span class="material-symbols-outlined">play_arrow</span> Run Tests';
    }
}

function displayTestResults(results) {
    const resultsDiv = document.getElementById('testResults');
    if (resultsDiv) {
        resultsDiv.classList.remove('hidden');
        
        // Handle error response
        if (results.error) {
            resultsDiv.innerHTML = `
                <div class="test-summary has-failures">
                    <h5>Test Error</h5>
                    <div class="test-error">${results.error}</div>
                </div>
            `;
            return;
        }
        
        const passed = results.passed || 0;
        const failed = results.failed || 0;
        const total = passed + failed;
        
        resultsDiv.innerHTML = `
            <div class="test-summary ${failed > 0 ? 'has-failures' : 'all-passed'}">
                <h5>Test Results</h5>
                <div class="test-stats">
                    <span class="passed">✓ ${passed} passed</span>
                    ${failed > 0 ? `<span class="failed">✗ ${failed} failed</span>` : ''}
                    <span class="total">${total} total</span>
                </div>
                <div class="test-info">
                    ${results.framework ? `<div class="test-framework">Framework: ${results.framework}</div>` : ''}
                    ${results.docker ? `<div class="test-docker">✓ Ran in Docker container</div>` : ''}
                </div>
                ${results.details && results.details.length > 0 ? `
                    <details class="test-details">
                        <summary>Test Details</summary>
                        <ul>
                            ${results.details.map(test => `
                                <li class="${test.outcome}">
                                    <span class="test-name">${test.name}</span>
                                    <span class="test-duration">${(test.duration || 0).toFixed(3)}s</span>
                                </li>
                            `).join('')}
                        </ul>
                    </details>
                ` : ''}
            </div>
            ${results.output ? `<pre class="test-output">${results.output}</pre>` : ''}
        `;
    }
}

// Reset Workflow
function resetWorkflow() {
    if (confirm('Are you sure you want to reset the entire workflow? All progress will be lost.')) {
        // Clear the workflow state
        window.workflow.state = {
            repoUrl: '',
            branch: 'main',
            vibe: '',
            plannerOutput: '',
            currentStep: 1,
            jobId: null,
            sessionId: null,
            lastCommitSha: null
        };
        
        // Clear the UI - check if elements exist before setting values
        const elements = {
            'githubUrlInputRepo': { type: 'value', value: '' },
            'githubBranch': { type: 'value', value: 'main' },
            'vibeStatement': { type: 'value', value: '' },
            'sectionAOutput': { type: 'textContent', value: '' },
            'sectionBOutput': { type: 'textContent', value: '' },
            'plannerInput': { type: 'value', value: '' },
            'feedbackText': { type: 'value', value: '' },
            'iterationPlannerInput': { type: 'value', value: '' },
            'iterationPlannerOutput': { type: 'textContent', value: '' },
            'iterationCoderOutput': { type: 'textContent', value: '' },
            'refinedPromptText': { type: 'textContent', value: '' }
        };
        
        for (const [id, config] of Object.entries(elements)) {
            const element = document.getElementById(id);
            if (element) {
                if (config.type === 'value') {
                    element.value = config.value;
                } else {
                    element.textContent = config.value;
                }
            }
        }
        
        // Clear and hide results sections
        const testResults = document.getElementById('testResults');
        if (testResults) {
            testResults.innerHTML = '';
            testResults.classList.add('hidden');
        }
        
        const commitHistory = document.getElementById('commitHistory');
        if (commitHistory) {
            commitHistory.innerHTML = '';
            commitHistory.classList.add('hidden');
        }
        
        const refinedPromptSection = document.getElementById('refinedPromptSection');
        if (refinedPromptSection) {
            refinedPromptSection.classList.add('hidden');
        }
        
        // Reset step visibility
        window.workflow.showStep(1);
        window.workflow.updateProgressIndicator();
        window.workflow.saveState();
        
        // Clear localStorage
        localStorage.removeItem('workflowState');
        
        alert('Workflow has been reset.');
    }
}

// Commit History Functions
async function viewCommits() {
    const commitBtn = event.target;
    commitBtn.disabled = true;
    
    try {
        console.log('Fetching commits with:', {
            repo_path: window.workflow.state.repoUrl,
            branch: window.workflow.state.branch,
            session_id: window.workflow.state.sessionId
        });
        
        const response = await fetch('/api/get-commits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                repo_path: window.workflow.state.repoUrl,
                branch: window.workflow.state.branch,
                session_id: window.workflow.state.sessionId
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Commits result:', result);
        displayCommitHistory(result.commits || result);
        
    } catch (error) {
        console.error('Error fetching commits:', error);
        const historyDiv = document.getElementById('commitHistory');
        if (historyDiv) {
            historyDiv.classList.remove('hidden');
            historyDiv.innerHTML = `<div class="error-message">
                <span class="material-symbols-outlined">error</span>
                Error: ${error.message}
            </div>`;
        }
    } finally {
        commitBtn.disabled = false;
    }
}

function displayCommitHistory(commits) {
    const historyDiv = document.getElementById('commitHistory');
    if (historyDiv) {
        historyDiv.classList.remove('hidden');
        
        // Handle both array and object response formats
        if (!commits || (Array.isArray(commits) && commits.length === 0)) {
            historyDiv.innerHTML = '<p>No commits found</p>';
            return;
        }
        
        // Ensure commits is an array
        const commitArray = Array.isArray(commits) ? commits : [];
        
        const commitList = commitArray.map(commit => `
            <div class="commit-item">
                <div class="commit-header">
                    <code class="commit-sha">${commit.sha.substring(0, 7)}</code>
                    <span class="commit-author">${commit.author}</span>
                    <span class="commit-date">${new Date(commit.timestamp * 1000).toLocaleDateString()}</span>
                </div>
                <div class="commit-message">${commit.message}</div>
                ${commit.diff ? `
                    <details class="commit-diff">
                        <summary>View Diff</summary>
                        <pre>${commit.diff}</pre>
                    </details>
                ` : ''}
            </div>
        `).join('');
        
        historyDiv.innerHTML = `
            <h5>Recent Commits</h5>
            <div class="commit-list">${commitList}</div>
        `;
        
        // Store the latest commit SHA for iteration
        if (commits.length > 0) {
            window.workflow.state.lastCommitSha = commits[0].sha;
            window.workflow.saveState();
        }
    }
}

// Utility Functions
function copyToClipboard(elementId, buttonElement) {
    const element = document.getElementById(elementId);
    if (element) {
        const text = element.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const btn = buttonElement;
            const originalText = btn.textContent;
            btn.textContent = 'Copied!';
            btn.style.background = '#10b981';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 1500);
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard');
        });
    }
}

function startIteration() {
    window.workflow.showStep(5);
    document.getElementById('stepIteration').classList.remove('hidden');
    
    // Fetch latest diff if we have a commit SHA
    if (window.workflow.state.lastCommitSha) {
        fetchLatestDiff();
    }
}

async function fetchLatestDiff() {
    try {
        const response = await fetch('/api/get-diff', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                repo_path: window.workflow.state.repoUrl,
                sha: window.workflow.state.lastCommitSha,
                session_id: window.workflow.state.sessionId
            })
        });
        
        const diff = await response.json();
        window.workflow.displayDiff(diff);
        
    } catch (error) {
        console.error('Error fetching diff:', error);
    }
}

// Refine prompt helper functions
function acceptRefinedPrompt() {
    const vibeInput = document.getElementById('vibeStatement');
    const refinedSection = document.getElementById('refinedPromptSection');
    const refinedText = document.getElementById('refinedPromptText');
    
    // Update the vibe statement with refined version
    vibeInput.value = refinedText.textContent;
    window.workflow.state.vibe = refinedText.textContent;
    window.workflow.saveState();
    
    // Hide the refined prompt section
    refinedSection.classList.add('hidden');
}

function rejectRefinedPrompt() {
    const refinedSection = document.getElementById('refinedPromptSection');
    
    // Simply hide the refined prompt section without updating
    refinedSection.classList.add('hidden');
    
    // Clear the refined vibe from state
    window.workflow.state.refinedVibe = '';
    window.workflow.saveState();
}

// Check LLM Status
async function checkLLMStatus() {
    try {
        const response = await fetch('/api/check-llm-status');
        const status = await response.json();
        
        if (status.success) {
            let message = "LLM API Status:\n\n";
            
            // Check environment variables
            message += "Environment Variables:\n";
            for (const [key, value] of Object.entries(status.env_vars)) {
                message += `${key}: ${value ? '✓ Set' : '✗ Not Set'}\n`;
            }
            
            message += "\nProviders:\n";
            for (const [provider, info] of Object.entries(status.providers)) {
                message += `${provider}:\n`;
                message += `  Configured: ${info.configured ? 'Yes' : 'No'}\n`;
                message += `  Available: ${info.available ? 'Yes' : 'No'}\n`;
                if (info.error) {
                    message += `  Error: ${info.error}\n`;
                }
            }
            
            alert(message);
        } else {
            alert('Error checking LLM status: ' + status.error);
        }
    } catch (error) {
        alert('Failed to check LLM status: ' + error.message);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.workflow = new WorkflowController();
});