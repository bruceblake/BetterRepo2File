// Vibe Coder Loop JavaScript
class VibeCoderLoop {
    constructor() {
        this.iteration = 1;
        this.lastCommitHash = null;
        this.featureVibe = '';
        this.plannerOutput = '';
        this.isLoopRunning = false;
        this.pollInterval = null;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Loop control buttons
        const startLoopBtn = document.getElementById('startLoop');
        const pauseLoopBtn = document.getElementById('pauseLoop');
        const stopLoopBtn = document.getElementById('stopLoop');
        
        if (startLoopBtn) {
            startLoopBtn.addEventListener('click', () => this.startLoop());
        }
        
        if (pauseLoopBtn) {
            pauseLoopBtn.addEventListener('click', () => this.pauseLoop());
        }
        
        if (stopLoopBtn) {
            stopLoopBtn.addEventListener('click', () => this.stopLoop());
        }
        
        // Feature vibe input
        const featureVibeInput = document.getElementById('featureVibe');
        if (featureVibeInput) {
            featureVibeInput.addEventListener('input', (e) => {
                this.featureVibe = e.target.value;
            });
        }
        
        // Iteration manual trigger
        const nextIterationBtn = document.getElementById('nextIteration');
        if (nextIterationBtn) {
            nextIterationBtn.addEventListener('click', () => this.triggerIteration());
        }
    }
    
    async startLoop() {
        this.isLoopRunning = true;
        this.updateLoopControls();
        
        // Start watching for commits
        this.pollInterval = setInterval(() => this.checkForNewCommits(), 30000); // Check every 30 seconds
        
        // Update status
        this.updateLoopStatus('running', 'Watching for commits...');
        
        // If no initial plan exists, create one
        if (!this.plannerOutput && this.featureVibe) {
            await this.generateInitialPlan();
        }
    }
    
    pauseLoop() {
        this.isLoopRunning = false;
        this.updateLoopControls();
        
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        
        this.updateLoopStatus('paused', 'Loop paused');
    }
    
    stopLoop() {
        this.isLoopRunning = false;
        this.updateLoopControls();
        
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        
        this.updateLoopStatus('stopped', 'Loop stopped');
        
        // Archive current feature if completed
        if (confirm('Archive this feature?')) {
            this.archiveFeature();
        }
    }
    
    updateLoopControls() {
        const startBtn = document.getElementById('startLoop');
        const pauseBtn = document.getElementById('pauseLoop');
        const stopBtn = document.getElementById('stopLoop');
        
        if (this.isLoopRunning) {
            if (startBtn) startBtn.classList.add('hidden');
            if (pauseBtn) pauseBtn.classList.remove('hidden');
            if (stopBtn) stopBtn.classList.remove('hidden');
        } else {
            if (startBtn) startBtn.classList.remove('hidden');
            if (pauseBtn) pauseBtn.classList.add('hidden');
            if (stopBtn) stopBtn.classList.add('hidden');
        }
    }
    
    updateLoopStatus(status, message) {
        const statusElement = document.querySelector('.loop-status');
        if (statusElement) {
            statusElement.className = `loop-status ${status}`;
            statusElement.textContent = message;
        }
        
        // Update iteration counter
        const iterationElement = document.querySelector('.iteration-count');
        if (iterationElement) {
            iterationElement.textContent = `Iteration: ${this.iteration}`;
        }
    }
    
    async checkForNewCommits() {
        try {
            const response = await fetch('/api/watch-commits/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    repo_path: '.',
                    last_commit: this.lastCommitHash
                })
            });
            
            const data = await response.json();
            
            if (data.commits && data.commits.length > 0) {
                // New commits detected
                const latestCommit = data.commits[0];
                this.lastCommitHash = latestCommit.hash;
                
                // Analyze the diff
                await this.analyzeDiff(latestCommit.hash);
                
                // Check if tests are passing
                const testResults = await this.runTests();
                
                // Trigger iteration if needed
                if (this.shouldTriggerIteration(testResults)) {
                    await this.triggerIteration();
                }
            }
        } catch (error) {
            console.error('Error checking for commits:', error);
        }
    }
    
    async analyzeDiff(commitHash) {
        try {
            const response = await fetch('/api/analyze-diff', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    repo_path: '.',
                    commit_hash: commitHash
                })
            });
            
            const data = await response.json();
            this.lastDiffSummary = data.summary;
            
            // Update UI with diff summary
            this.updateDiffSummary(data.summary);
            
        } catch (error) {
            console.error('Error analyzing diff:', error);
        }
    }
    
    async runTests() {
        try {
            const response = await fetch('/api/run-tests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    repo_path: '.',
                    framework: 'auto'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                return data.results;
            } else {
                console.error('Test run failed:', data.error);
                return {
                    passed: 0,
                    failed: 0,
                    errors: 1,
                    failure_details: [data.error]
                };
            }
        } catch (error) {
            console.error('Error running tests:', error);
            return {
                passed: 0,
                failed: 0,
                errors: 1,
                failure_details: ['Failed to connect to test runner']
            };
        }
    }
    
    shouldTriggerIteration(testResults) {
        // Trigger iteration if:
        // 1. Tests are failing
        // 2. No changes in last 10 minutes (configurable)
        // 3. Manual trigger requested
        
        return testResults.failed > 0 || testResults.errors > 0;
    }
    
    async triggerIteration() {
        this.iteration++;
        this.updateLoopStatus('processing', 'Generating iteration brief...');
        
        try {
            // Generate iteration brief
            const iterationBrief = await this.generateIterationBrief();
            
            // Start new analysis with Section C
            await this.startIterationAnalysis(iterationBrief);
            
            this.updateLoopStatus('running', 'Iteration in progress...');
            
        } catch (error) {
            console.error('Error triggering iteration:', error);
            this.updateLoopStatus('error', 'Error during iteration');
        }
    }
    
    async generateIterationBrief() {
        const response = await fetch('/api/generate-iteration-brief', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                planner_output: this.plannerOutput,
                diff_summary: this.lastDiffSummary,
                test_results: await this.runTests(),
                feature_vibe: this.featureVibe
            })
        });
        
        const data = await response.json();
        return data.iteration_brief;
    }
    
    async startIterationAnalysis(iterationBrief) {
        const formData = new FormData();
        formData.append('vibe', this.featureVibe);
        formData.append('stage', 'C');
        formData.append('iteration_brief', iterationBrief);
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        // Handle job tracking similar to main workflow
    }
    
    async generateInitialPlan() {
        this.updateLoopStatus('processing', 'Generating initial plan...');
        
        const formData = new FormData();
        formData.append('vibe', this.featureVibe);
        formData.append('stage', 'A');
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        // Handle job tracking and save planner output
    }
    
    updateDiffSummary(summary) {
        const diffElement = document.getElementById('diffSummary');
        if (diffElement) {
            diffElement.innerHTML = `
                <h4>Latest Changes</h4>
                <p>Files changed: ${summary.files_changed.join(', ')}</p>
                <p>Lines added: ${summary.additions}, deleted: ${summary.deletions}</p>
                ${summary.functions_modified.length > 0 ? 
                    `<p>Functions modified: ${summary.functions_modified.join(', ')}</p>` : ''}
                <div class="summary-text">${summary.high_level_summary}</div>
            `;
        }
    }
    
    async archiveFeature() {
        try {
            const response = await fetch('/api/archive-feature', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feature_vibe: this.featureVibe,
                    planner_outputs: [this.plannerOutput],  // Can add more iterations
                    commits: this.commitHistory || [],
                    test_results: await this.runTests()
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Feature archived:', data.archive_id);
                alert(`Feature archived successfully! Archive ID: ${data.archive_id}`);
                
                // Reset state for next feature
                this.reset();
            } else {
                console.error('Archive failed:', data.error);
                alert('Failed to archive feature: ' + data.error);
            }
        } catch (error) {
            console.error('Error archiving feature:', error);
            alert('Error archiving feature');
        }
    }
    
    reset() {
        this.iteration = 1;
        this.lastCommitHash = null;
        this.featureVibe = '';
        this.plannerOutput = '';
        this.isLoopRunning = false;
        this.commitHistory = [];
        
        // Clear UI elements
        const featureVibeInput = document.getElementById('featureVibe');
        if (featureVibeInput) {
            featureVibeInput.value = '';
        }
        
        // Reset dashboard
        document.getElementById('loop-dashboard')?.classList.add('hidden');
        
        // Show initial step
        window.vibeCoderApp?.resetWizard();
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.vibeCoderLoop = new VibeCoderLoop();
});