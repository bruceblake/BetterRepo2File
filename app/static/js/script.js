// Virtual scrolling configuration
const VIRTUAL_SCROLL_THRESHOLD = 5000000; // 5MB
const CHUNK_SIZE = 100000; // 100KB chunks

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const githubUrlInput = document.getElementById('githubUrlInput');
    const fileTypesInput = document.getElementById('fileTypes');
    const useGitignoreCheckbox = document.getElementById('useGitignore');
    const smartModeCheckbox = document.getElementById('smartMode');
    const tokenModeCheckbox = document.getElementById('tokenMode');
    const ultraModeCheckbox = document.getElementById('ultraMode');
    const ultraSettings = document.getElementById('ultraSettings');
    const llmModelSelect = document.getElementById('llmModel');
    const tokenBudgetInput = document.getElementById('tokenBudget');
    const vibeStatementInput = document.getElementById('vibeStatement');
    const plannerOutputInput = document.getElementById('plannerOutput');
    const processBtn = document.getElementById('processBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const outputSection = document.getElementById('outputSection');
    const outputContent = document.getElementById('outputContent');
    const exclusionInfo = document.getElementById('exclusionInfo');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const profileSelect = document.getElementById('profileSelect');
    
    // Track operation ID for downloading
    let currentOperationId = null;
    
    // Track uploaded files
    let uploadedFiles = [];
    
    // Checkbox interactions
    tokenModeCheckbox.addEventListener('change', function() {
        if (this.checked) {
            smartModeCheckbox.checked = false;
            smartModeCheckbox.disabled = true;
            ultraModeCheckbox.checked = false;
            ultraModeCheckbox.disabled = true;
        } else {
            smartModeCheckbox.disabled = false;
            ultraModeCheckbox.disabled = false;
        }
    });
    
    ultraModeCheckbox.addEventListener('change', function() {
        if (this.checked) {
            smartModeCheckbox.checked = false;
            smartModeCheckbox.disabled = true;
            tokenModeCheckbox.checked = false;
            tokenModeCheckbox.disabled = true;
            ultraSettings.classList.remove('hidden');
        } else {
            smartModeCheckbox.disabled = false;
            tokenModeCheckbox.disabled = false;
            ultraSettings.classList.add('hidden');
        }
    });
    
    smartModeCheckbox.addEventListener('change', function() {
        if (this.checked) {
            if (tokenModeCheckbox.checked) {
                tokenModeCheckbox.checked = false;
            }
            if (ultraModeCheckbox.checked) {
                ultraModeCheckbox.checked = false;
            }
        }
    });
    
    // Profile selection handler
    profileSelect.addEventListener('change', function() {
        const selectedProfile = this.value;
        
        if (selectedProfile === 'gemini') {
            // Enable ultra mode for Gemini profile
            ultraModeCheckbox.checked = true;
            ultraModeCheckbox.dispatchEvent(new Event('change'));
            
            // Set Gemini model and token budget
            llmModelSelect.value = 'gemini-1.5-pro';
            tokenBudgetInput.value = '1000000';
        } else if (selectedProfile === 'datascience') {
            // Data science profile uses ultra mode
            ultraModeCheckbox.checked = true;
            ultraModeCheckbox.dispatchEvent(new Event('change'));
            
            // Keep default model and token budget
            llmModelSelect.value = 'gpt-4';
            tokenBudgetInput.value = '500000';
        } else {
            // Other profiles use smart mode by default
            smartModeCheckbox.checked = true;
            ultraModeCheckbox.checked = false;
            ultraModeCheckbox.dispatchEvent(new Event('change'));
        }
    });
    
    // Tab switching with ARIA support
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Update active tab button and ARIA attributes
            tabBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-selected', 'false');
            });
            btn.classList.add('active');
            btn.setAttribute('aria-selected', 'true');
            
            // Show corresponding tab content
            tabContents.forEach(content => {
                if (content.id === tabId) {
                    content.classList.remove('hidden');
                    content.removeAttribute('hidden');
                } else {
                    content.classList.add('hidden');
                    content.setAttribute('hidden', 'true');
                }
            });
            
            // Focus management for accessibility
            const firstInput = document.querySelector(`#${tabId} input:not([hidden])`);
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        });
    });
    
    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.add('active');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.remove('active');
        });
    });
    
    dropArea.addEventListener('drop', handleDrop);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });
    
    function handleFiles(files) {
        if (files.length === 0) return;
        
        uploadedFiles = Array.from(files);
        updateFileList();
    }
    
    function updateFileList() {
        fileList.innerHTML = '';
        
        if (uploadedFiles.length === 0) {
            return;
        }
        
        uploadedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileName = document.createElement('div');
            fileName.className = 'file-name';
            fileName.textContent = file.name;
            
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-file';
            removeBtn.innerHTML = '&times;';
            removeBtn.setAttribute('aria-label', `Remove ${file.name}`);
            removeBtn.setAttribute('title', `Remove ${file.name}`);
            removeBtn.addEventListener('click', () => {
                uploadedFiles.splice(index, 1);
                updateFileList();
                
                // Announce removal to screen readers
                const announcement = document.createElement('div');
                announcement.textContent = `${file.name} removed from file list`;
                announcement.className = 'sr-only';
                announcement.setAttribute('role', 'status');
                announcement.setAttribute('aria-live', 'polite');
                document.body.appendChild(announcement);
                setTimeout(() => announcement.remove(), 1000);
            });
            
            fileItem.appendChild(fileName);
            fileItem.appendChild(removeBtn);
            fileList.appendChild(fileItem);
        });
    }
    
    // Process button click event
    processBtn.addEventListener('click', processInput);
    
    function processInput() {
        // Reset previous errors
        errorMessage.classList.add('hidden');
        
        // Check which tab is active
        const activeTab = document.querySelector('.tab-btn.active').getAttribute('data-tab');
        
        let formData = new FormData();
        
        // Add file types if provided
        if (fileTypesInput.value.trim()) {
            formData.append('file_types', fileTypesInput.value.trim());
        }
        
        // Add gitignore preference
        formData.append('use_gitignore', useGitignoreCheckbox.checked);
        
        // Add smart mode preference
        formData.append('smart_mode', smartModeCheckbox.checked);
        
        // Add token mode preference
        formData.append('token_mode', tokenModeCheckbox.checked);
        
        // Add ultra mode preference
        formData.append('ultra_mode', ultraModeCheckbox.checked);
        if (ultraModeCheckbox.checked) {
            formData.append('llm_model', llmModelSelect.value);
            formData.append('token_budget', tokenBudgetInput.value);
            
            // Add intended query if provided
            const intendedQuery = document.getElementById('intendedQuery').value.trim();
            if (intendedQuery) {
                formData.append('intended_query', intendedQuery);
            }
            
            // Add vibe statement if provided
            const vibeStatement = vibeStatementInput.value.trim();
            if (vibeStatement) {
                formData.append('vibe_statement', vibeStatement);
            }
            
            // Add planner output if provided
            const plannerOutput = plannerOutputInput.value.trim();
            if (plannerOutput) {
                formData.append('planner_output', plannerOutput);
            }
        }
        
        // Add profile if selected
        const selectedProfile = profileSelect.value;
        if (selectedProfile) {
            formData.append('profile', selectedProfile);
        }
        
        if (activeTab === 'file-upload') {
            // File upload mode
            if (uploadedFiles.length === 0) {
                showError('Please select files to process');
                return;
            }
            
            uploadedFiles.forEach(file => {
                formData.append('files[]', file);
            });
        } else {
            // GitHub URL mode
            const githubUrl = githubUrlInput.value.trim();
            if (!githubUrl) {
                showError('Please enter a GitHub repository URL');
                return;
            }
            
            if (!isValidGithubUrl(githubUrl)) {
                showError('Please enter a valid GitHub repository URL (e.g., https://github.com/username/repo)');
                return;
            }
            
            formData.append('github_url', githubUrl);
            
            // Add branch if specified
            const branchInput = document.getElementById('branchInput');
            const branch = branchInput.value.trim();
            if (branch) {
                formData.append('github_branch', branch);
            }
        }
        
        // Show loading indicator
        loadingIndicator.classList.remove('hidden');
        outputSection.classList.add('hidden');
        
        // Submit the form
        fetch('/process', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('hidden');
            
            if (data.error) {
                showError(data.error);
                return;
            }
            
            // Store the operation ID for download
            currentOperationId = data.operation_id;
            
            // Display the output with handling for large content
            if (data.content.length > 100000) {
                // For very large outputs, provide progressive loading feedback
                outputContent.textContent = 'Loading large output...';
                
                // Use setTimeout to let the UI update before setting the large content
                setTimeout(() => {
                    outputContent.textContent = data.content;
                    
                    // Add a warning about large content
                    const warningDiv = document.createElement('div');
                    warningDiv.className = 'large-content-warning';
                    warningDiv.innerHTML = `
                        <p>⚠️ Large output detected (${(data.content.length / 1024 / 1024).toFixed(2)} MB)</p>
                        <p>The browser may be slow to respond. Consider using the Download option for better performance.</p>
                    `;
                    outputContent.parentElement.insertBefore(warningDiv, outputContent);
                }, 100);
            } else {
                outputContent.textContent = data.content;
            }
            
            // Display exclusion file and mode information
            let info = [];
            if (data.used_gitignore) {
                info.push(`Using repository's .gitignore file`);
            } else {
                info.push(`Using default exclusion patterns (${data.exclusion_file})`);
            }
            
            if (data.ultra_mode) {
                info.push(`Ultra Mode: ${data.llm_model} with ${parseInt(data.token_budget).toLocaleString()} token budget`);
            } else if (data.token_mode) {
                info.push(`Token-Aware Mode: Ultra-optimized with 500K token budget`);
            } else if (data.smart_mode) {
                info.push(`Smart Mode: AI-optimized output`);
            } else {
                info.push(`Standard Mode`);
            }
            exclusionInfo.textContent = info.join(' • ');
            
            outputSection.classList.remove('hidden');
            
            // Update download button with file size
            const fileSizeBytes = new Blob([data.content]).size;
            const fileSizeMB = (fileSizeBytes / 1024 / 1024).toFixed(2);
            downloadBtn.textContent = `Download (${fileSizeMB} MB)`;
            
            // Scroll to output section
            outputSection.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            loadingIndicator.classList.add('hidden');
            showError('An error occurred: ' + error.message);
        });
    }
    
    function isValidGithubUrl(url) {
        return /^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-_.]+\/?.*$/.test(url);
    }
    
    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
    }
    
    // Copy button click event
    copyBtn.addEventListener('click', function() {
        // Handle large content copy with better error handling
        const content = outputContent.textContent;
        
        if (content.length > 1000000) {
            // For very large content, show warning
            if (!confirm('This is a large amount of text (' + (content.length / 1024 / 1024).toFixed(2) + ' MB). Copying may take a while or fail. Continue?')) {
                return;
            }
        }
        
        navigator.clipboard.writeText(content)
            .then(() => {
                // Visual feedback for copy success
                const originalText = copyBtn.textContent;
                const originalAriaLabel = copyBtn.getAttribute('aria-label');
                copyBtn.textContent = 'Copied!';
                copyBtn.setAttribute('aria-label', 'Successfully copied to clipboard');
                copyBtn.classList.add('success');
                
                // Announce to screen readers
                const announcement = document.createElement('div');
                announcement.textContent = 'Text successfully copied to clipboard';
                announcement.className = 'sr-only';
                announcement.setAttribute('role', 'status');
                announcement.setAttribute('aria-live', 'polite');
                document.body.appendChild(announcement);
                
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                    copyBtn.setAttribute('aria-label', originalAriaLabel);
                    copyBtn.classList.remove('success');
                    announcement.remove();
                }, 2000);
            })
            .catch(err => {
                showError('Failed to copy: ' + err);
                copyBtn.classList.add('error');
                setTimeout(() => copyBtn.classList.remove('error'), 2000);
            });
    });
    
    // Download button click event
    downloadBtn.addEventListener('click', function() {
        // Show loading state for large downloads
        const originalText = this.textContent;
        this.textContent = 'Preparing download...';
        this.disabled = true;
        
        if (!currentOperationId) {
            showError('No output available to download');
            return;
        }
        
        window.location.href = `/download/${currentOperationId}`;
        
        // Reset button after a short delay
        setTimeout(() => {
            this.textContent = originalText;
            this.disabled = false;
        }, 2000);
    });
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (currentOperationId) {
            // Use sendBeacon for more reliable cleanup during page navigation
            navigator.sendBeacon('/cleanup', JSON.stringify({ operation_id: currentOperationId }));
        }
    });
});