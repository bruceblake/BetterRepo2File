// Unified Repo2File Vibe Coder JavaScript
class VibeCoderApp {
    constructor() {
        this.currentStep = 1;
        this.state = {
            mode: 'vibe',
            stage: 'A', // Default to planning stage
            vibe: '',
            refinedVibe: '',
            repository: null,
            repoUrl: '',
            repoBranch: '',
            repoType: 'github', // Always github now
            dockerEnabled: false,
            dockerServices: [],
            dockerComposeFile: null,
            testCommand: '',
            plannerOutput: '',
            previousOutput: null,
            feedbackLog: null,
            jobId: null,
            sessionId: null
        };
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Mode selection
        document.querySelectorAll('.mode-card').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                
                const mode = card.id.replace('-mode', '');
                this.state.mode = mode;
                
                if (mode === 'vibe') {
                    document.getElementById('vibe-workflow').classList.remove('hidden');
                    document.getElementById('classic-workflow').classList.add('hidden');
                } else {
                    document.getElementById('classic-workflow').classList.remove('hidden');
                    document.getElementById('vibe-workflow').classList.add('hidden');
                }
            });
        });
        
        // Docker checkbox
        const dockerCheckbox = document.getElementById('useDocker');
        if (dockerCheckbox) {
            dockerCheckbox.addEventListener('change', (e) => {
                this.state.dockerEnabled = e.target.checked;
                const dockerConfig = document.getElementById('dockerConfig');
                if (this.state.dockerEnabled) {
                    dockerConfig.classList.remove('hidden');
                } else {
                    dockerConfig.classList.add('hidden');
                }
            });
        }
        
        // Docker compose file upload
        const composeFile = document.getElementById('composeFile');
        if (composeFile) {
            composeFile.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.parseDockerCompose(file);
                }
            });
        }
        
        // Test command input
        const testCommandInput = document.getElementById('testCommand');
        if (testCommandInput) {
            testCommandInput.addEventListener('input', (e) => {
                this.state.testCommand = e.target.value;
            });
        }
        
        // Docker test service selector
        const dockerTestService = document.getElementById('dockerTestService');
        if (dockerTestService) {
            dockerTestService.addEventListener('change', (e) => {
                this.state.dockerTestService = e.target.value;
            });
        }
        
        // Drop area
        const dropArea = document.getElementById('dropArea');
        if (dropArea) {
            dropArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropArea.classList.add('drag-over');
            });
            
            dropArea.addEventListener('dragleave', () => {
                dropArea.classList.remove('drag-over');
            });
            
            dropArea.addEventListener('drop', (e) => {
                e.preventDefault();
                dropArea.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileUpload(files[0]);
                }
            });
        }
        
        // File input
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileUpload(e.target.files[0]);
                }
            });
        }
        
        // GitHub URL input
        const githubUrlInput = document.getElementById('githubUrlInputRepo');
        if (githubUrlInput) {
            githubUrlInput.addEventListener('input', (e) => {
                this.state.repoUrl = e.target.value.trim();
                console.log('GitHub URL updated:', this.state.repoUrl);
                
                // Clear refined vibe when repository changes
                this.state.refinedVibe = '';
                const refinedDiv = document.getElementById('refinedVibe');
                if (refinedDiv) {
                    refinedDiv.classList.add('hidden');
                }
            });
        }
        
        // GitHub branch input
        const githubBranchInput = document.getElementById('githubBranch');
        if (githubBranchInput) {
            githubBranchInput.addEventListener('input', (e) => {
                this.state.repoBranch = e.target.value.trim();
                console.log('GitHub branch updated:', this.state.repoBranch);
            });
        }
        
        // Vibe statement
        const vibeTextarea = document.getElementById('featureVibe');
        if (vibeTextarea) {
            vibeTextarea.addEventListener('input', (e) => {
                this.state.vibe = e.target.value;
                const charCount = e.target.parentElement.querySelector('.char-count');
                if (charCount) {
                    charCount.textContent = `${e.target.value.length} characters`;
                }
                
                // Clear refined vibe when vibe changes significantly
                if (this.state.refinedVibe && 
                    !this.state.vibe.includes(this.state.refinedVibe.substring(0, 50))) {
                    this.state.refinedVibe = '';
                    const refinedDiv = document.getElementById('refinedVibe');
                    if (refinedDiv) {
                        refinedDiv.classList.add('hidden');
                    }
                }
            });
        }
        
        
        // Stage selection
        document.querySelectorAll('.stage-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.stage-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                this.state.stage = card.getAttribute('data-stage');
                
                // Dispatch stage change event for Vibe Guide
                const stageMapping = {
                    'A': 'planning',
                    'B': 'coding',
                    'C': 'iteration'
                };
                const event = new CustomEvent('vibeStageChanged', {
                    detail: { stage: stageMapping[this.state.stage] }
                });
                document.dispatchEvent(event);
            });
        });
        
        // Next/Previous buttons
        document.querySelectorAll('.next-btn').forEach(btn => {
            btn.addEventListener('click', () => this.nextStep());
        });
        
        document.querySelectorAll('.prev-btn').forEach(btn => {
            btn.addEventListener('click', () => this.previousStep());
        });
        
        // Generate buttons
        const generateBtn = document.querySelector('.generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.startAnalysis());
        }
        
        // Generate context button (step 3)
        const generateContextBtn = document.querySelector('.generate-context-btn');
        if (generateContextBtn) {
            console.log('Generate context button found, attaching listener');
            generateContextBtn.addEventListener('click', () => {
                console.log('Generate context button clicked');
                this.state.stage = 'A';
                this.startAnalysis();
            });
        } else {
            console.error('Generate context button not found!')
        }
        
        // Generate coding button (step 4)
        const generateCodingBtn = document.querySelector('.generate-coding-btn');
        if (generateCodingBtn) {
            generateCodingBtn.addEventListener('click', () => {
                this.state.stage = 'B';
                this.startAnalysis();
            });
        }
        
        // Planner input choice
        document.querySelectorAll('.choice-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const choice = btn.getAttribute('data-choice');
                document.querySelectorAll('.choice-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                if (choice === 'paste') {
                    document.getElementById('plannerText').classList.remove('hidden');
                    document.getElementById('plannerFile').classList.add('hidden');
                } else {
                    document.getElementById('plannerText').classList.add('hidden');
                    document.getElementById('plannerFile').classList.remove('hidden');
                }
            });
        });
        
        // Result tabs
        document.querySelectorAll('.result-tabs .tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.getAttribute('data-tab');
                
                document.querySelectorAll('.result-tabs .tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                document.querySelectorAll('.result-content').forEach(content => {
                    content.classList.add('hidden');
                });
                
                const targetContent = document.getElementById(tab);
                if (targetContent) {
                    targetContent.classList.remove('hidden');
                }
            });
        });
        
        // Copy button
        const copyBtn = document.querySelector('.copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyToClipboard());
        }
        
        // New analysis button
        const newAnalysisBtn = document.querySelector('.new-analysis');
        if (newAnalysisBtn) {
            newAnalysisBtn.addEventListener('click', () => window.location.reload());
        }
        
        // Mark feature complete button
        const markCompleteBtn = document.querySelector('.mark-feature-done');
        if (markCompleteBtn) {
            markCompleteBtn.addEventListener('click', () => {
                window.vibeCoderLoop?.archiveFeature();
            });
        }
    }
    
    resetWizard() {
        this.currentStep = 1;
        this.state = {
            mode: 'vibe',
            stage: null,
            vibe: '',
            repository: null,
            dockerEnabled: false,
            dockerServices: [],
            plannerOutput: '',
            previousOutput: null,
            feedbackLog: null,
            jobId: null
        };
        
        // Reset UI to initial state
        this.updateStepVisibility();
        this.updateStepIndicators();
        
        // Clear form fields
        document.getElementById('vibeStatement').value = '';
        document.getElementById('useDocker').checked = false;
        
        // Reset mode cards
        document.querySelectorAll('.mode-card').forEach(card => {
            card.classList.remove('active');
        });
        document.getElementById('vibe-mode').classList.add('active');
        
        // Show vibe workflow
        document.getElementById('vibe-workflow').classList.remove('hidden');
        document.getElementById('classic-workflow').classList.add('hidden');
        document.getElementById('results').classList.add('hidden');
    }
    
    handleFileUpload(file) {
        this.state.repository = file;
        
        // Update UI to show file name
        const dropArea = document.getElementById('dropArea');
        const message = dropArea.querySelector('.drop-message');
        message.innerHTML = `<p>Selected: ${file.name}</p><p>Size: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>`;
    }
    
    async parseDockerCompose(file) {
        const formData = new FormData();
        formData.append('compose_file', file);
        
        try {
            const response = await fetch('/api/parse-compose', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            this.state.dockerServices = data.services;
            
            // Update UI with services
            const servicesList = document.getElementById('dockerServices');
            servicesList.innerHTML = '<h4>Services detected:</h4>';
            data.services.forEach(service => {
                servicesList.innerHTML += `<div class="service-item">
                    <input type="checkbox" id="service-${service}" value="${service}" checked>
                    <label for="service-${service}">${service}</label>
                </div>`;
            });
        } catch (error) {
            console.error('Error parsing docker-compose:', error);
        }
    }
    
    nextStep() {
        if (this.validateCurrentStep()) {
            this.currentStep++;
            this.updateStepVisibility();
            this.updateStepIndicators();
            
            // Update summary on final step
            if (this.currentStep === 4) {
                this.updateSummary();
            }
        }
    }
    
    previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepVisibility();
            this.updateStepIndicators();
        }
    }
    
    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                // Capture GitHub repository URL and branch
                const githubUrlInput = document.getElementById('githubUrlInputRepo');
                const githubBranchInput = document.getElementById('githubBranch');
                
                if (githubUrlInput) {
                    this.state.repoUrl = githubUrlInput.value.trim();
                }
                if (githubBranchInput && githubBranchInput.value.trim()) {
                    this.state.repoBranch = githubBranchInput.value.trim();
                }
                
                // Validate feature vibe and repository selection
                if (!this.state.vibe) {
                    alert('Please describe your feature/goal');
                    return false;
                }
                if (!this.state.repoUrl) {
                    alert('Please enter a GitHub repository URL');
                    return false;
                }
                // Validate GitHub URL format
                const githubUrlPattern = /^https:\/\/github\.com\/[\w-]+\/[\w-]+$/;
                if (!githubUrlPattern.test(this.state.repoUrl)) {
                    alert('Please enter a valid GitHub repository URL (e.g., https://github.com/username/repo)');
                    return false;
                }
                return true;
            case 2:
                // Repository setup - no additional validation needed
                return true;
            case 3:
                // Planning phase - set stage to A automatically
                this.state.stage = 'A';
                return true;
            case 4:
                // Coding phase - set stage to B and validate planner output
                this.state.stage = 'B';
                const plannerText = document.getElementById('plannerText');
                const plannerFile = document.getElementById('plannerFile');
                if (plannerText && !plannerText.value && plannerFile && !plannerFile.files[0]) {
                    alert('Please provide planner output');
                    return false;
                }
                return true;
            case 5:
                // Loop phase - set stage to C
                this.state.stage = 'C';
                return true;
            default:
                return true;
        }
    }
    
    updateStepVisibility() {
        document.querySelectorAll('.wizard-content').forEach(content => {
            content.classList.add('hidden');
        });
        
        const currentContent = document.querySelector(`.wizard-content[data-step="${this.currentStep}"]`);
        if (currentContent) {
            currentContent.classList.remove('hidden');
        }
        
        // If we just moved to step 2, detect docker-compose
        if (this.currentStep === 2 && this.state.repoUrl) {
            this.detectDockerCompose();
        }
        
        // Show stage-specific inputs
        if (this.currentStep === 3) {
            document.querySelectorAll('.stage-input').forEach(input => {
                input.classList.add('hidden');
            });
            
            if (this.state.stage === 'B') {
                document.getElementById('stage-b-input').classList.remove('hidden');
            } else if (this.state.stage === 'C') {
                document.getElementById('stage-c-input').classList.remove('hidden');
            }
        }
        
        // If we just moved to step 4, populate the planner output
        if (this.currentStep === 4) {
            console.log('At step 4, checking planner output');
            if (this.state.plannerOutput) {
                console.log('Has planner output, trying to populate textarea');
                const plannerText = document.getElementById('plannerText');
                if (plannerText) {
                    plannerText.value = this.state.plannerOutput;
                    console.log('Populated textarea with planner output');
                } else {
                    console.error('plannerText element not found!');
                }
            } else {
                console.log('No planner output in state');
            }
        }
    }
    
    updateStepIndicators() {
        document.querySelectorAll('.step').forEach((step, index) => {
            if (index + 1 <= this.currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }
    
    updateSummary() {
        // Update repository summary
        let repoSummary = 'None';
        if (this.state.repoType === 'local' && this.state.repoPath) {
            repoSummary = `Local: ${this.state.repoPath}`;
        } else if (this.state.repoType === 'github' && this.state.repoUrl) {
            repoSummary = `GitHub: ${this.state.repoUrl}`;
        } else if (this.state.repository) {
            repoSummary = this.state.repository.name;
        }
        document.getElementById('repoSummary').textContent = repoSummary;
        
        document.getElementById('vibeSummary').textContent = this.state.vibe || 'None';
        
        const stageMap = { 'A': 'Plan', 'B': 'Code', 'C': 'Iterate' };
        document.getElementById('stageSummary').textContent = stageMap[this.state.stage] || 'None';
        
        if (this.state.dockerEnabled) {
            document.getElementById('dockerSummary').classList.remove('hidden');
            document.getElementById('dockerServices').textContent = this.state.dockerServices.join(', ') || 'None';
        }
    }
    
    async startAnalysis() {
        console.log('Starting analysis with state:', this.state);
        
        // Validate vibe matches repository
        if (this.state.repoUrl && this.state.vibe) {
            const repoName = this.state.repoUrl.split('/').pop().replace('.git', '');
            const owner = this.state.repoUrl.split('/').slice(-2)[0];
            const fullRepoName = `${owner}/${repoName}`;
            
            // Check if vibe references a different repository
            if ((this.state.vibe.includes('github.com') && !this.state.vibe.includes(this.state.repoUrl)) ||
                (this.state.vibe.includes('MintWebsite') && !this.state.repoUrl.includes('MintWebsite'))) {
                console.warn('Vibe statement appears to reference a different repository');
                // Clear the vibe to force user to update it
                alert('Your feature description appears to reference a different repository. Please update it to match your selected repository.');
                return;
            }
        }
        
        const formData = new FormData();
        
        // Add basic data
        formData.append('vibe', this.state.vibe);
        formData.append('stage', this.state.stage);
        
        console.log('Sending request with stage:', this.state.stage);
        
        // Add repository information
        console.log('Adding repository info - URL:', this.state.repoUrl, 'Branch:', this.state.repoBranch);
        formData.append('repo_type', 'github');
        if (this.state.repoUrl) {
            formData.append('repo_url', this.state.repoUrl);
        } else {
            console.error('WARNING: No repository URL in state!');
        }
        if (this.state.repoBranch) {
            formData.append('repo_branch', this.state.repoBranch);
        }
        
        // Add legacy repository support (files)
        if (this.state.repository) {
            formData.append('repo_zip', this.state.repository);
        }
        
        // Add stage-specific data
        if (this.state.stage === 'B') {
            const plannerText = document.getElementById('plannerText').value;
            if (plannerText) {
                formData.append('planner_output', plannerText);
            } else {
                const plannerFile = document.getElementById('plannerFile').files[0];
                if (plannerFile) {
                    formData.append('planner_file', plannerFile);
                }
            }
        } else if (this.state.stage === 'C') {
            const previousOutput = document.getElementById('previousOutput').files[0];
            if (previousOutput) {
                formData.append('previous_output', previousOutput);
            }
            const feedbackLog = document.getElementById('feedbackLog').files[0];
            if (feedbackLog) {
                formData.append('feedback_log', feedbackLog);
            }
        }
        
        // Add test configuration
        if (this.state.testCommand) {
            formData.append('test_command', this.state.testCommand);
        }
        
        // Add Docker data
        if (this.state.dockerEnabled) {
            formData.append('docker_enabled', 'true');
            formData.append('docker_services', JSON.stringify(this.state.dockerServices));
            if (this.state.dockerTestService) {
                formData.append('docker_test_service', this.state.dockerTestService);
            }
        }
        
        // Show progress overlay
        this.showProgress();
        
        try {
            // Start analysis
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            this.state.jobId = data.job_id;
            if (data.session_id) {
                this.state.sessionId = data.session_id;
                window.unifiedState.sessionId = data.session_id; // Update exposed state
            }
            
            // Start listening for progress updates
            this.listenForProgress();
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.hideProgress();
            alert('Failed to start analysis: ' + error.message);
        }
    }
    
    listenForProgress() {
        console.log('Starting EventSource for job:', this.state.jobId);
        const eventSource = new EventSource(`/api/status/${this.state.jobId}`);
        
        eventSource.onmessage = (event) => {
            console.log('Progress event:', event.data);
            const data = JSON.parse(event.data);
            
            if (data.error) {
                console.error('Progress error:', data.error);
                eventSource.close();
                this.hideProgress();
                alert('Analysis failed: ' + data.error);
                return;
            }
            
            if (data.phase === 'completed') {
                console.log('Analysis completed, fetching results');
                eventSource.close();
                this.fetchResults();
                return;
            }
            
            // Check for keepalive
            if (data.keepalive) {
                console.log('Keepalive received');
                return;
            }
            
            // Update progress UI
            this.updateProgress(data);
        };
        
        eventSource.onerror = (error) => {
            console.error('EventSource error:', error, 'readyState:', eventSource.readyState);
            eventSource.close();
            this.hideProgress();
        };
    }
    
    updateProgress(data) {
        const message = document.getElementById('progressMessage');
        const stats = document.getElementById('progressStats');
        
        if (message) {
            message.textContent = data.phase || 'Processing...';
        }
        
        if (stats) {
            stats.textContent = `${data.current || 0} / ${data.total || 0} files processed`;
        }
        
        // Update progress bar
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill && data.total > 0) {
            const percentage = (data.current / data.total) * 100;
            progressFill.style.width = `${percentage}%`;
        }
    }
    
    async fetchResults() {
        try {
            console.log('Fetching results for job:', this.state.jobId);
            const response = await fetch(`/api/result/${this.state.jobId}`);
            const result = await response.json();
            
            console.log('Fetched result:', result);
            this.hideProgress();
            this.showResults(result);
            
        } catch (error) {
            console.error('Failed to fetch results:', error);
            this.hideProgress();
            alert('Failed to fetch results: ' + error.message);
        }
    }
    
    showResults(result) {
        console.log('showResults called with:', result);
        console.log('Current stage:', this.state.stage, 'Current step:', this.currentStep);
        
        if (this.state.stage === 'A' && this.currentStep === 3) {
            // For stage A (planning), advance to next step
            console.log('Advancing to step 4 with Section A content');
            
            // Store the Section A content FIRST before updating UI
            if (result.copy_text) {
                this.state.plannerOutput = result.copy_text;
                console.log('Stored planner output:', this.state.plannerOutput.substring(0, 100) + '...');
            } else {
                console.error('No copy_text in result!');
            }
            
            this.hideProgress();
            this.currentStep++;
            this.updateStepVisibility();
            this.updateStepIndicators();
            
            return;
        }
        
        // For other stages, show results
        // Hide wizard
        document.getElementById('vibe-workflow').classList.add('hidden');
        
        // Show results
        document.getElementById('results').classList.remove('hidden');
        
        // Populate copy section
        const copyContent = document.getElementById('copyContent');
        if (copyContent) {
            copyContent.textContent = result.copy_text || '';
        }
        
        // Populate manifest
        const manifestContent = document.querySelector('.file-tree');
        if (manifestContent) {
            manifestContent.innerHTML = result.manifest_html || '';
        }
        
        // Populate stats
        document.getElementById('filesCount').textContent = result.stats?.files_processed || '0';
        document.getElementById('tokensUsed').textContent = result.stats?.used || '0';
        document.getElementById('filesSkipped').textContent = result.stats?.skipped || '0';
        
        // Populate skip report
        const skipList = document.getElementById('skipList');
        if (skipList && result.skipped_files) {
            skipList.innerHTML = result.skipped_files.map(file => 
                `<li>${file.path} - ${file.reason}</li>`
            ).join('');
        }
        
        // Set up Docker logs if enabled
        if (this.state.dockerEnabled) {
            this.setupDockerLogs();
        }
    }
    
    setupDockerLogs() {
        const serviceSelector = document.getElementById('serviceSelector');
        
        // Populate service selector
        this.state.dockerServices.forEach(service => {
            const option = document.createElement('option');
            option.value = service;
            option.textContent = service;
            serviceSelector.appendChild(option);
        });
        
        // Handle service selection
        serviceSelector.addEventListener('change', () => {
            this.fetchServiceLogs(serviceSelector.value);
        });
        
        // Handle refresh button
        document.querySelector('.refresh-logs').addEventListener('click', () => {
            this.fetchServiceLogs(serviceSelector.value);
        });
    }
    
    async fetchServiceLogs(service) {
        if (!service) return;
        
        try {
            const response = await fetch(`/api/docker/logs/${service}`);
            const data = await response.json();
            
            const logContent = document.getElementById('logContent');
            if (logContent) {
                logContent.textContent = data.logs;
                // Auto-scroll to bottom
                logContent.parentElement.scrollTop = logContent.parentElement.scrollHeight;
            }
        } catch (error) {
            console.error('Failed to fetch logs:', error);
        }
    }
    
    async copyToClipboard() {
        const content = document.getElementById('copyContent').textContent;
        
        try {
            await navigator.clipboard.writeText(content);
            
            // Show success feedback
            const copyBtn = document.querySelector('.copy-btn');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.style.background = 'var(--theme-success-color)';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '';
            }, 2000);
            
        } catch (error) {
            console.error('Failed to copy:', error);
            alert('Failed to copy to clipboard');
        }
    }
    
    showProgress() {
        document.getElementById('progressOverlay').classList.remove('hidden');
    }
    
    hideProgress() {
        document.getElementById('progressOverlay').classList.add('hidden');
    }
    
    async detectDockerCompose() {
        try {
            const response = await fetch('/api/detect-docker-compose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_url: this.state.repoUrl,
                    repo_branch: this.state.repoBranch
                })
            });
            
            const data = await response.json();
            
            if (data.has_compose) {
                this.state.dockerComposeFile = data.compose_file;
                this.state.dockerServices = data.services;
                
                // Update UI
                const dockerCheckbox = document.getElementById('useDocker');
                if (dockerCheckbox) {
                    dockerCheckbox.checked = true;
                    this.state.dockerEnabled = true;
                    
                    // Show docker config
                    const dockerConfig = document.getElementById('dockerConfig');
                    dockerConfig.classList.remove('hidden');
                    
                    // Show services section
                    const servicesSection = document.querySelector('.docker-services-section');
                    servicesSection.classList.remove('hidden');
                    
                    // Populate services list
                    const servicesList = document.getElementById('dockerServices');
                    servicesList.innerHTML = data.services.map(service => 
                        `<div class="service-item">${service}</div>`
                    ).join('');
                    
                    // Populate service selector
                    const serviceSelect = document.getElementById('dockerTestService');
                    serviceSelect.innerHTML = '<option value="">Select a service</option>';
                    data.services.forEach(service => {
                        const option = document.createElement('option');
                        option.value = service;
                        option.textContent = service;
                        serviceSelect.appendChild(option);
                    });
                }
            }
        } catch (error) {
            console.error('Failed to detect docker-compose:', error);
        }
    }
}

// Global functions for HTML onclick
async function refineVibe() {
    const vibeTextarea = document.getElementById('featureVibe');
    const vibe = vibeTextarea.value.trim();
    
    if (!vibe) {
        alert('Please enter a feature description first');
        return;
    }
    
    // Validate repository selection
    const app = window.vibeCoderApp;
    if (app.state.repoType === 'local' && !app.state.repoPath) {
        alert('Please enter a local repository path first');
        return;
    }
    if (app.state.repoType === 'github' && !app.state.repoUrl) {
        alert('Please enter a GitHub repository URL first');
        return;
    }
    
    // Get repository context
    const repoInfo = app.state.repoType === 'local' 
        ? { type: 'local', path: app.state.repoPath }
        : { type: 'github', url: app.state.repoUrl };
    
    try {
        // Show loading state
        const refineBtn = document.querySelector('.refine-btn');
        refineBtn.disabled = true;
        refineBtn.innerHTML = '<span class="material-symbols-outlined">hourglass_empty</span> Analyzing...';
        
        const response = await fetch('/api/refine-prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt_text: vibe,
                repo_info: repoInfo,
                target: 'planning'
            })
        });
        
        const data = await response.json();
        
        if (data.refined_prompt) {
            // Show refined vibe
            const refinedDiv = document.getElementById('refinedVibe');
            refinedDiv.innerHTML = `
                <h4>AI-Refined Feature Description</h4>
                <div class="vibe-content">${data.refined_prompt}</div>
                <div class="actions">
                    <button class="use-btn" onclick="useRefinedVibe()">Use This</button>
                    <button class="cancel-btn" onclick="cancelRefinedVibe()">Cancel</button>
                </div>
            `;
            refinedDiv.classList.remove('hidden');
            
            // Store in app state
            window.vibeCoderApp.state.refinedVibe = data.refined_prompt;
        } else {
            alert('Failed to refine prompt: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error refining vibe:', error);
        alert('Error connecting to refinement service');
    } finally {
        // Reset button state
        const refineBtn = document.querySelector('.refine-btn');
        refineBtn.disabled = false;
        refineBtn.innerHTML = '<span class="material-symbols-outlined">auto_awesome</span> Refine with AI';
    }
}

function useRefinedVibe() {
    const vibeTextarea = document.getElementById('featureVibe');
    vibeTextarea.value = window.vibeCoderApp.state.refinedVibe;
    window.vibeCoderApp.state.vibe = window.vibeCoderApp.state.refinedVibe;
    
    // Clear any old repository references
    if (window.vibeCoderApp.state.repoUrl) {
        // Check if the refined vibe matches the current repository
        const repoName = window.vibeCoderApp.state.repoUrl.split('/').pop().replace('.git', '');
        if (!window.vibeCoderApp.state.refinedVibe.includes(repoName)) {
            console.warn('Refined vibe may not match current repository');
        }
    }
    
    // Update character count
    const charCount = document.querySelector('.char-count');
    if (charCount) {
        charCount.textContent = `${vibeTextarea.value.length} characters`;
    }
    
    cancelRefinedVibe();
}

function cancelRefinedVibe() {
    const refinedDiv = document.getElementById('refinedVibe');
    refinedDiv.classList.add('hidden');
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.vibeCoderApp = new VibeCoderApp();
    window.unifiedState = window.vibeCoderApp.state; // Expose state for other components
});

// Clear all state and restart
function clearAndRestart() {
    if (confirm('This will clear all current progress and start fresh. Continue?')) {
        // Clear local storage
        localStorage.clear();
        
        // Clear session storage
        sessionStorage.clear();
        
        // Clear any cached data
        if (window.vibeCoderApp) {
            window.vibeCoderApp.state = {
                mode: 'vibe',
                stage: 'A',
                vibe: '',
                refinedVibe: '',
                repository: null,
                repoUrl: '',
                repoBranch: '',
                repoType: 'github',
                dockerEnabled: false,
                dockerServices: [],
                dockerComposeFile: null,
                testCommand: '',
                plannerOutput: '',
                previousOutput: null,
                feedbackLog: null,
                jobId: null,
                sessionId: null
            };
            window.vibeCoderApp.currentStep = 1;
        }
        
        // Reload the page
        window.location.reload();
    }
}