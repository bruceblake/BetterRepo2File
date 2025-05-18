// Unified Repo2File Vibe Coder JavaScript
class VibeCoderApp {
    constructor() {
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
        
        // Tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = btn.getAttribute('data-tab');
                const parent = btn.closest('.tabs');
                
                // Update active states
                parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Show/hide content
                const section = parent.nextElementSibling;
                while (section && section.classList.contains('tab-content')) {
                    section.classList.add('hidden');
                    section = section.nextElementSibling;
                }
                
                const content = document.getElementById(tab);
                if (content) {
                    content.classList.remove('hidden');
                }
            });
        });
        
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
        
        // Vibe statement
        const vibeTextarea = document.getElementById('vibeStatement');
        if (vibeTextarea) {
            vibeTextarea.addEventListener('input', (e) => {
                this.state.vibe = e.target.value;
                const charCount = e.target.parentElement.querySelector('.char-count');
                if (charCount) {
                    charCount.textContent = `${e.target.value.length} characters`;
                }
            });
        }
        
        // Stage selection
        document.querySelectorAll('.stage-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.stage-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                this.state.stage = card.getAttribute('data-stage');
            });
        });
        
        // Next/Previous buttons
        document.querySelectorAll('.next-btn').forEach(btn => {
            btn.addEventListener('click', () => this.nextStep());
        });
        
        document.querySelectorAll('.prev-btn').forEach(btn => {
            btn.addEventListener('click', () => this.previousStep());
        });
        
        // Generate button
        const generateBtn = document.querySelector('.generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.startAnalysis());
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
                if (!this.state.repository && !document.getElementById('githubUrl').value && !document.getElementById('localPath')?.value) {
                    alert('Please select a repository');
                    return false;
                }
                if (!this.state.vibe) {
                    alert('Please describe your vibe/goal');
                    return false;
                }
                return true;
            case 2:
                if (!this.state.stage) {
                    alert('Please select a stage');
                    return false;
                }
                return true;
            case 3:
                // Stage-specific validation
                if (this.state.stage === 'B' && !this.state.plannerOutput && !document.getElementById('plannerFile').files[0]) {
                    alert('Please provide planner output');
                    return false;
                }
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
        document.getElementById('repoSummary').textContent = 
            this.state.repository ? this.state.repository.name : 
            document.getElementById('githubUrl').value || 
            document.getElementById('localPath')?.value || 'None';
        
        document.getElementById('vibeSummary').textContent = this.state.vibe || 'None';
        
        const stageMap = { 'A': 'Plan', 'B': 'Code', 'C': 'Iterate' };
        document.getElementById('stageSummary').textContent = stageMap[this.state.stage] || 'None';
        
        if (this.state.dockerEnabled) {
            document.getElementById('dockerSummary').classList.remove('hidden');
            document.getElementById('dockerServices').textContent = this.state.dockerServices.join(', ') || 'None';
        }
    }
    
    async startAnalysis() {
        const formData = new FormData();
        
        // Add basic data
        formData.append('vibe', this.state.vibe);
        formData.append('stage', this.state.stage);
        
        // Add repository
        if (this.state.repository) {
            formData.append('repo_zip', this.state.repository);
        } else {
            const githubUrl = document.getElementById('githubUrl').value;
            if (githubUrl) {
                formData.append('github_url', githubUrl);
                const branch = document.getElementById('githubBranch').value;
                if (branch) {
                    formData.append('github_branch', branch);
                }
            }
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
        
        // Add Docker data
        if (this.state.dockerEnabled) {
            formData.append('docker_enabled', 'true');
            formData.append('docker_services', JSON.stringify(this.state.dockerServices));
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
            
            // Start listening for progress updates
            this.listenForProgress();
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.hideProgress();
            alert('Failed to start analysis: ' + error.message);
        }
    }
    
    listenForProgress() {
        const eventSource = new EventSource(`/api/status/${this.state.jobId}`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                console.error('Progress error:', data.error);
                eventSource.close();
                this.hideProgress();
                alert('Analysis failed: ' + data.error);
                return;
            }
            
            if (data.phase === 'completed') {
                eventSource.close();
                this.fetchResults();
                return;
            }
            
            // Update progress UI
            this.updateProgress(data);
        };
        
        eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
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
            const response = await fetch(`/api/result/${this.state.jobId}`);
            const result = await response.json();
            
            this.hideProgress();
            this.showResults(result);
            
        } catch (error) {
            console.error('Failed to fetch results:', error);
            this.hideProgress();
            alert('Failed to fetch results: ' + error.message);
        }
    }
    
    showResults(result) {
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
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VibeCoderApp();
});