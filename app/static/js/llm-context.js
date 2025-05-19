// LLM Context Generation Functions

// Load predefined LLM profiles
async function loadLLMProfile(profileName) {
    try {
        const response = await fetch('/api/llm/task-profiles');
        const data = await response.json();
        
        if (data.profiles && data.profiles[profileName]) {
            const profile = data.profiles[profileName];
            
            // Set form values from profile
            document.getElementById('llm-task-type').value = profile.task_type;
            document.getElementById('llm-model').value = profile.model;
            document.getElementById('llm-token-budget').value = profile.token_budget;
            document.getElementById('llm-output-format').value = profile.output_format;
            document.getElementById('llm-focus-areas').value = profile.focus_areas.join(', ');
            
            // Set checkboxes
            if (profile.options) {
                document.getElementById('llm-include-tests').checked = profile.options.include_tests || false;
                document.getElementById('llm-semantic-analysis').checked = profile.options.semantic_analysis || false;
            }
            
            showToast(`Loaded ${profileName} profile`, 'success');
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        showToast('Failed to load profile', 'error');
    }
}

// Preview LLM context without generating
async function previewLLMContext() {
    const repoUrl = document.getElementById('githubUrlInputRepo')?.value;
    const branch = document.getElementById('githubBranch')?.value || 'main';
    
    if (!repoUrl) {
        showToast('Please enter a GitHub repository URL', 'error');
        return;
    }
    
    const params = {
        repository_path: repoUrl,
        task_type: document.getElementById('llm-task-type').value,
        model: document.getElementById('llm-model').value,
        token_budget: parseInt(document.getElementById('llm-token-budget').value),
        output_format: document.getElementById('llm-output-format').value
    };
    
    // Add focus areas if specified
    const focusAreas = document.getElementById('llm-focus-areas').value.trim();
    if (focusAreas) {
        params.focus_areas = focusAreas.split(',').map(s => s.trim());
    }
    
    try {
        showLoader('Generating preview...');
        
        const response = await fetch('/api/llm/preview-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            throw new Error(`Preview failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Show preview in modal
        document.getElementById('preview-tokens').textContent = data.estimated_tokens.toLocaleString();
        document.getElementById('preview-files').textContent = data.included_files;
        document.getElementById('preview-total').textContent = data.total_files;
        document.getElementById('preview-content').textContent = data.preview;
        
        document.getElementById('llm-preview-modal').style.display = 'flex';
        
        hideLoader();
    } catch (error) {
        console.error('Preview error:', error);
        hideLoader();
        showToast(`Preview failed: ${error.message}`, 'error');
    }
}

// Close preview modal
function closeLLMPreview() {
    document.getElementById('llm-preview-modal').style.display = 'none';
}

// Generate LLM context
async function generateLLMContext() {
    const repoUrl = document.getElementById('githubUrlInputRepo')?.value;
    const branch = document.getElementById('githubBranch')?.value || 'main';
    
    if (!repoUrl) {
        showToast('Please enter a GitHub repository URL', 'error');
        return;
    }
    
    const params = {
        repository_path: repoUrl,
        task_type: document.getElementById('llm-task-type').value,
        model: document.getElementById('llm-model').value,
        token_budget: parseInt(document.getElementById('llm-token-budget').value),
        output_format: document.getElementById('llm-output-format').value,
        options: {
            include_prompt: document.getElementById('llm-include-prompt').checked,
            include_tests: document.getElementById('llm-include-tests').checked,
            semantic_analysis: document.getElementById('llm-semantic-analysis').checked
        }
    };
    
    // Add focus areas if specified
    const focusAreas = document.getElementById('llm-focus-areas').value.trim();
    if (focusAreas) {
        params.focus_areas = focusAreas.split(',').map(s => s.trim());
    }
    
    try {
        showLoader('Generating LLM context...');
        
        const response = await fetch('/api/llm/generate-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            throw new Error(`Generation failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Store job info
        window.llmJobId = data.job_id;
        
        // Update UI
        document.getElementById('llm-job-id').textContent = data.job_id;
        document.getElementById('llm-status').textContent = 'Processing...';
        document.getElementById('llm-results').style.display = 'block';
        
        // Start polling for job status
        pollLLMJobStatus(data.job_id);
        
        hideLoader();
        showToast('LLM context generation started', 'success');
        
    } catch (error) {
        console.error('Generation error:', error);
        hideLoader();
        showToast(`Generation failed: ${error.message}`, 'error');
    }
}

// Poll for job status
async function pollLLMJobStatus(jobId) {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/jobs/${jobId}/status`);
            const data = await response.json();
            
            document.getElementById('llm-status').textContent = data.state;
            
            if (data.state === 'SUCCESS') {
                clearInterval(pollInterval);
                document.getElementById('llm-status').textContent = 'Completed';
                showToast('LLM context generation completed', 'success');
                
                // Store result for download
                window.llmResult = data.result;
            } else if (data.state === 'FAILURE') {
                clearInterval(pollInterval);
                document.getElementById('llm-status').textContent = 'Failed';
                showToast(`Generation failed: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Status polling error:', error);
        }
    }, 2000);
}

// Download LLM context
async function downloadLLMContext() {
    if (!window.llmResult || !window.llmResult.output_files) {
        showToast('No context available to download', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/jobs/${window.llmJobId}/download`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `llm_context_${window.llmJobId}.${document.getElementById('llm-output-format').value}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('Context downloaded', 'success');
    } catch (error) {
        console.error('Download error:', error);
        showToast('Failed to download context', 'error');
    }
}

// Copy LLM context to clipboard
async function copyLLMContext() {
    if (!window.llmResult || !window.llmResult.output_files) {
        showToast('No context available to copy', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/jobs/${window.llmJobId}/download`);
        const text = await response.text();
        
        await navigator.clipboard.writeText(text);
        showToast('Context copied to clipboard', 'success');
    } catch (error) {
        console.error('Copy error:', error);
        showToast('Failed to copy context', 'error');
    }
}

// View LLM context
async function viewLLMContext() {
    if (!window.llmResult || !window.llmResult.output_files) {
        showToast('No context available to view', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/jobs/${window.llmJobId}/download`);
        const text = await response.text();
        
        // Create a modal or open in new tab
        const viewWindow = window.open('', '_blank');
        viewWindow.document.write(`
            <html>
                <head>
                    <title>LLM Context - ${window.llmJobId}</title>
                    <style>
                        body { font-family: monospace; padding: 20px; }
                        pre { white-space: pre-wrap; word-wrap: break-word; }
                    </style>
                </head>
                <body>
                    <h1>LLM Context</h1>
                    <p>Job ID: ${window.llmJobId}</p>
                    <p>Task Type: ${document.getElementById('llm-task-type').value}</p>
                    <p>Model: ${document.getElementById('llm-model').value}</p>
                    <hr>
                    <pre>${escapeHtml(text)}</pre>
                </body>
            </html>
        `);
        
    } catch (error) {
        console.error('View error:', error);
        showToast('Failed to view context', 'error');
    }
}

// Helper functions
function showLoader(message) {
    // Implementation depends on your UI framework
    console.log('Loader:', message);
}

function hideLoader() {
    // Implementation depends on your UI framework
    console.log('Loader hidden');
}

function showToast(message, type) {
    // Implementation depends on your UI framework
    console.log(`Toast [${type}]:`, message);
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check if LLM section exists
    if (document.getElementById('llm-context-step')) {
        console.log('LLM context features initialized');
    }
});