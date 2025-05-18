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
    const processBtn = document.getElementById('processBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const outputSection = document.getElementById('outputSection');
    const outputContent = document.getElementById('outputContent');
    const exclusionInfo = document.getElementById('exclusionInfo');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
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
    
    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show corresponding tab content
            tabContents.forEach(content => {
                if (content.id === tabId) {
                    content.classList.remove('hidden');
                } else {
                    content.classList.add('hidden');
                }
            });
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
            removeBtn.addEventListener('click', () => {
                uploadedFiles.splice(index, 1);
                updateFileList();
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
            
            // Display the output
            outputContent.textContent = data.content;
            
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
        navigator.clipboard.writeText(outputContent.textContent)
            .then(() => {
                // Visual feedback for copy success
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                showError('Failed to copy: ' + err);
            });
    });
    
    // Download button click event
    downloadBtn.addEventListener('click', function() {
        if (!currentOperationId) {
            showError('No output available to download');
            return;
        }
        
        window.location.href = `/download/${currentOperationId}`;
    });
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (currentOperationId) {
            // Use sendBeacon for more reliable cleanup during page navigation
            navigator.sendBeacon('/cleanup', JSON.stringify({ operation_id: currentOperationId }));
        }
    });
});