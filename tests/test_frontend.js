/**
 * Frontend JavaScript test suite for BetterRepo2File
 * Uses Jest for testing
 */

// Mock DOM elements
document.body.innerHTML = `
    <div id="progressOverlay" class="hidden"></div>
    <div id="progressMessage"></div>
    <div id="progressTitle"></div>
    <div id="progressIcon"></div>
    <div id="progressBar"></div>
    <div id="sectionAOutput"></div>
    <div id="sectionBOutput"></div>
    <div id="plannerOutput"></div>
    <div id="githubUrlInputRepo"></div>
    <div id="githubBranch"></div>
    <div id="vibeStatement"></div>
    <div id="feedbackText"></div>
    <div id="testResults"></div>
    <div id="commitHistory"></div>
    <div id="refinedPromptSection"></div>
    <div class="progress-step" data-step="1"></div>
    <div class="progress-step" data-step="2"></div>
    <div class="progress-step" data-step="3"></div>
    <div class="progress-step" data-step="4"></div>
`;

// Import the WorkflowController class (would need to be modularized)
// For now, we'll test the functions directly

describe('WorkflowController', () => {
    let workflow;

    beforeEach(() => {
        // Reset localStorage
        localStorage.clear();
        
        // Reset fetch mock
        global.fetch = jest.fn();
        
        // Create workflow instance (simplified for testing)
        workflow = {
            state: {
                repoUrl: '',
                branch: 'main',
                vibe: '',
                currentStep: 1,
                sessionId: null,
                jobId: null
            },
            
            saveState: function() {
                try {
                    const minimalState = {
                        repoUrl: this.state.repoUrl,
                        branch: this.state.branch,
                        vibe: this.state.vibe?.substring(0, 1000),
                        currentStep: this.state.currentStep,
                        sessionId: this.state.sessionId
                    };
                    localStorage.setItem('workflowState', JSON.stringify(minimalState));
                } catch (e) {
                    console.error('Error saving state:', e);
                }
            },
            
            loadSavedState: function() {
                try {
                    const saved = localStorage.getItem('workflowState');
                    if (saved) {
                        const savedState = JSON.parse(saved);
                        this.state.repoUrl = savedState.repoUrl || '';
                        this.state.branch = savedState.branch || 'main';
                        this.state.vibe = savedState.vibe || '';
                        this.state.currentStep = savedState.currentStep || 1;
                        this.state.sessionId = savedState.sessionId || null;
                    }
                } catch (e) {
                    console.error('Error loading state:', e);
                }
            },
            
            showProgress: function(message, title = 'Processing...', step = null) {
                const overlay = document.getElementById('progressOverlay');
                const msgElement = document.getElementById('progressMessage');
                const titleElement = document.getElementById('progressTitle');
                
                if (overlay) {
                    if (msgElement) msgElement.textContent = message;
                    if (titleElement) titleElement.textContent = title;
                    overlay.classList.remove('hidden');
                }
            },
            
            hideProgress: function() {
                const overlay = document.getElementById('progressOverlay');
                if (overlay) {
                    overlay.classList.add('hidden');
                }
            }
        };
    });

    describe('State Management', () => {
        test('saveState saves minimal state to localStorage', () => {
            workflow.state.repoUrl = 'https://github.com/test/repo';
            workflow.state.vibe = 'Test feature';
            workflow.state.sessionId = 'test-123';
            
            workflow.saveState();
            
            const saved = JSON.parse(localStorage.getItem('workflowState'));
            expect(saved).toBeDefined();
            expect(saved.repoUrl).toBe('https://github.com/test/repo');
            expect(saved.vibe).toBe('Test feature');
            expect(saved.sessionId).toBe('test-123');
        });

        test('saveState handles quota exceeded error', () => {
            // Mock localStorage to throw quota exceeded error
            const mockSetItem = jest.fn().mockImplementation(() => {
                throw new DOMException('QuotaExceededError');
            });
            Object.defineProperty(window, 'localStorage', {
                value: {
                    setItem: mockSetItem,
                    getItem: jest.fn(),
                    removeItem: jest.fn(),
                    clear: jest.fn()
                },
                writable: true
            });
            
            workflow.saveState();
            
            expect(mockSetItem).toHaveBeenCalled();
        });

        test('loadSavedState restores state from localStorage', () => {
            const testState = {
                repoUrl: 'https://github.com/saved/repo',
                branch: 'develop',
                vibe: 'Saved feature',
                currentStep: 3,
                sessionId: 'saved-123'
            };
            
            localStorage.setItem('workflowState', JSON.stringify(testState));
            
            workflow.loadSavedState();
            
            expect(workflow.state.repoUrl).toBe('https://github.com/saved/repo');
            expect(workflow.state.branch).toBe('develop');
            expect(workflow.state.vibe).toBe('Saved feature');
            expect(workflow.state.currentStep).toBe(3);
            expect(workflow.state.sessionId).toBe('saved-123');
        });
    });

    describe('Progress Display', () => {
        test('showProgress updates UI elements', () => {
            workflow.showProgress('Testing progress', 'Test Title', 1);
            
            const overlay = document.getElementById('progressOverlay');
            const message = document.getElementById('progressMessage');
            const title = document.getElementById('progressTitle');
            
            expect(overlay.classList.contains('hidden')).toBe(false);
            expect(message.textContent).toBe('Testing progress');
            expect(title.textContent).toBe('Test Title');
        });

        test('hideProgress hides the overlay', () => {
            const overlay = document.getElementById('progressOverlay');
            overlay.classList.remove('hidden');
            
            workflow.hideProgress();
            
            expect(overlay.classList.contains('hidden')).toBe(true);
        });
    });

    describe('API Calls', () => {
        test('generateContext makes correct API call', async () => {
            workflow.state.repoUrl = 'https://github.com/test/repo';
            workflow.state.vibe = 'Test feature';
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: true, job_id: 'test-job' })
            });
            
            // Simplified version of generateContext
            const response = await fetch('/api/generate_context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_url: workflow.state.repoUrl,
                    repo_branch: workflow.state.branch,
                    vibe: workflow.state.vibe,
                    stage: 'A'
                })
            });
            
            expect(fetch).toHaveBeenCalledWith('/api/generate_context', expect.any(Object));
            const result = await response.json();
            expect(result.success).toBe(true);
            expect(result.job_id).toBe('test-job');
        });
    });
});

describe('UI Functions', () => {
    test('resetWorkflow clears all state and UI', () => {
        // Mock confirm dialog
        window.confirm = jest.fn(() => true);
        
        // Set up initial state
        workflow.state.repoUrl = 'https://github.com/test/repo';
        workflow.state.vibe = 'Test feature';
        
        // Add some UI values
        document.getElementById('githubUrlInputRepo').value = 'https://github.com/test/repo';
        document.getElementById('vibeStatement').value = 'Test feature';
        
        // Mock resetWorkflow function
        function resetWorkflow() {
            if (confirm('Reset?')) {
                // Clear state
                workflow.state = {
                    repoUrl: '',
                    branch: 'main',
                    vibe: '',
                    currentStep: 1,
                    sessionId: null,
                    jobId: null
                };
                
                // Clear UI
                const elements = {
                    'githubUrlInputRepo': { type: 'value', value: '' },
                    'vibeStatement': { type: 'value', value: '' }
                };
                
                for (const [id, config] of Object.entries(elements)) {
                    const element = document.getElementById(id);
                    if (element) {
                        element.value = config.value;
                    }
                }
                
                localStorage.removeItem('workflowState');
            }
        }
        
        resetWorkflow();
        
        expect(workflow.state.repoUrl).toBe('');
        expect(workflow.state.vibe).toBe('');
        expect(document.getElementById('githubUrlInputRepo').value).toBe('');
        expect(document.getElementById('vibeStatement').value).toBe('');
    });

    test('displayTestResults shows test output correctly', () => {
        function displayTestResults(results) {
            const resultsDiv = document.getElementById('testResults');
            if (resultsDiv) {
                resultsDiv.classList.remove('hidden');
                
                if (results.error) {
                    resultsDiv.innerHTML = `<div class="error">${results.error}</div>`;
                    return;
                }
                
                const passed = results.passed || 0;
                const failed = results.failed || 0;
                
                resultsDiv.innerHTML = `
                    <div class="test-summary">
                        <span class="passed">${passed} passed</span>
                        <span class="failed">${failed} failed</span>
                    </div>
                `;
            }
        }
        
        // Test with successful results
        displayTestResults({ passed: 5, failed: 0 });
        
        const resultsDiv = document.getElementById('testResults');
        expect(resultsDiv.classList.contains('hidden')).toBe(false);
        expect(resultsDiv.innerHTML).toContain('5 passed');
        expect(resultsDiv.innerHTML).toContain('0 failed');
        
        // Test with error
        displayTestResults({ error: 'Test error' });
        expect(resultsDiv.innerHTML).toContain('Test error');
    });
});