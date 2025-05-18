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
        this.loadSavedState();
        this.updateProgressIndicator();
        this.showStep(this.state.currentStep); // Make sure the current step is visible
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
        
        document.getElementById('plannerOutput')?.addEventListener('input', (e) => {
            this.state.plannerOutput = e.target.value;
            this.saveState();
        });
    }
    
    saveState() {
        localStorage.setItem('workflowState', JSON.stringify(this.state));
    }
    
    loadSavedState() {
        const saved = localStorage.getItem('workflowState');
        if (saved) {
            this.state = { ...this.state, ...JSON.parse(saved) };
            this.restoreInputs();
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
        
        const step = document.getElementById(`step${stepNumber}`);
        if (step) {
            step.classList.remove('hidden');
        }
        
        this.state.currentStep = stepNumber;
        this.updateProgressIndicator();
        this.saveState();
    }
    
    showProgress(message) {
        const overlay = document.getElementById('progressOverlay');
        const msgElement = document.getElementById('progressMessage');
        
        if (overlay && msgElement) {
            msgElement.textContent = message;
            overlay.classList.remove('hidden');
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
        
        this.showProgress('Cloning repository and generating context...');
        
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
        if (!this.state.plannerOutput) {
            alert('Please paste the AI planner output first');
            return;
        }
        
        this.showProgress('Generating implementation context...');
        
        try {
            const response = await fetch('/api/generate_context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_url: this.state.repoUrl,
                    repo_branch: this.state.branch,
                    vibe: this.state.vibe,
                    stage: 'B',
                    planner_output: this.state.plannerOutput
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
        
        this.showProgress('Generating context for Gemini re-planning...');
        
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
                    previous_planner_output: this.state.plannerOutput,
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
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.phase) {
                this.showProgress(data.phase.charAt(0).toUpperCase() + data.phase.slice(1) + '...');
            }
            
            if (data.status === 'completed') {
                eventSource.close();
                this.displayResults(data.result);
                this.hideProgress();
            } else if (data.error) {
                eventSource.close();
                alert('Error: ' + data.error);
                this.hideProgress();
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
        
        this.state.iterationPlannerOutput = iterationPlannerInput;
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
async function runTests() {
    const testBtn = event.target;
    testBtn.disabled = true;
    testBtn.innerHTML = '<span class="material-symbols-outlined">pending</span> Running...';
    
    try {
        const response = await fetch('/api/run-tests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                repo_path: window.workflow.state.repoUrl,
                session_id: window.workflow.state.sessionId
            })
        });
        
        const result = await response.json();
        displayTestResults(result);
        
    } catch (error) {
        alert('Error running tests: ' + error.message);
    } finally {
        testBtn.disabled = false;
        testBtn.innerHTML = '<span class="material-symbols-outlined">play_arrow</span> Run Tests';
    }
}

function displayTestResults(results) {
    const resultsDiv = document.getElementById('testResults');
    if (resultsDiv) {
        resultsDiv.classList.remove('hidden');
        
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
            </div>
            ${results.output ? `<pre class="test-output">${results.output}</pre>` : ''}
        `;
    }
}

// Commit History Functions
async function viewCommits() {
    const commitBtn = event.target;
    commitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/get-commits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                repo_path: window.workflow.state.repoUrl,
                branch: window.workflow.state.branch,
                session_id: window.workflow.state.sessionId
            })
        });
        
        const commits = await response.json();
        displayCommitHistory(commits);
        
    } catch (error) {
        alert('Error fetching commits: ' + error.message);
    } finally {
        commitBtn.disabled = false;
    }
}

function displayCommitHistory(commits) {
    const historyDiv = document.getElementById('commitHistory');
    if (historyDiv) {
        historyDiv.classList.remove('hidden');
        
        if (!commits || commits.length === 0) {
            historyDiv.innerHTML = '<p>No commits found</p>';
            return;
        }
        
        const commitList = commits.map(commit => `
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