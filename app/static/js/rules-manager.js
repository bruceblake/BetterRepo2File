// Rules Management JavaScript
class RulesManager {
    constructor() {
        this.selectedRules = [];
        this.ruleFiles = [];
        this.init();
    }
    
    async init() {
        // Load existing rules when tab is opened
        const rulesTab = document.querySelector('[data-tab="rules"]');
        if (rulesTab) {
            rulesTab.addEventListener('click', () => {
                this.loadProjectRules();
            });
        }
    }
    
    async loadProjectRules() {
        try {
            const response = await fetch('/api/list-rules');
            const data = await response.json();
            
            if (data.success) {
                this.ruleFiles = data.rules;
                this.renderRulesList();
            }
        } catch (error) {
            console.error('Error loading rules:', error);
        }
    }
    
    renderRulesList() {
        const rulesList = document.getElementById('rulesList');
        if (!rulesList) return;
        
        if (this.ruleFiles.length === 0) {
            rulesList.innerHTML = `
                <p class="no-rules">No rules found. Create a markdown file in the 'instructions' folder or import a template.</p>
            `;
            return;
        }
        
        rulesList.innerHTML = this.ruleFiles.map(rule => `
            <div class="rule-item">
                <input type="checkbox" id="rule-${rule.id}" value="${rule.filename}"
                    ${this.selectedRules.includes(rule.filename) ? 'checked' : ''}
                    onchange="rulesManager.toggleRule('${rule.filename}')">
                <label for="rule-${rule.id}">${rule.name}</label>
                <span class="rule-size">${this.formatSize(rule.size)}</span>
            </div>
        `).join('');
    }
    
    toggleRule(filename) {
        const index = this.selectedRules.indexOf(filename);
        if (index > -1) {
            this.selectedRules.splice(index, 1);
        } else {
            this.selectedRules.push(filename);
        }
        
        this.updateSelectedRulesDisplay();
        
        // Store in app state for use during context generation
        if (window.vibeCoderApp) {
            window.vibeCoderApp.state.selectedRules = this.selectedRules;
        }
    }
    
    updateSelectedRulesDisplay() {
        const selectedList = document.getElementById('selectedRulesList');
        if (!selectedList) return;
        
        if (this.selectedRules.length === 0) {
            selectedList.innerHTML = '<p class="no-selection">No rules selected</p>';
            return;
        }
        
        selectedList.innerHTML = this.selectedRules.map(filename => `
            <span class="selected-rule-chip">${this.getNameFromFilename(filename)}</span>
        `).join('');
    }
    
    getNameFromFilename(filename) {
        return filename.replace('.md', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
    
    async showTemplateModal() {
        try {
            const response = await fetch('/api/list-rule-templates');
            const data = await response.json();
            
            if (data.success) {
                this.renderTemplateModal(data.templates);
            }
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }
    
    renderTemplateModal(templates) {
        const modal = document.createElement('div');
        modal.className = 'rule-template-modal';
        modal.innerHTML = `
            <div class="rule-template-content">
                <div class="rule-template-header">
                    <h3>Import Rule Template</h3>
                    <button class="template-close-btn" onclick="rulesManager.closeTemplateModal()">✕</button>
                </div>
                <div class="template-list">
                    ${templates.map(template => `
                        <div class="template-item" onclick="rulesManager.importTemplate('${template.filename}')">
                            <h4>${template.name}</h4>
                            <p>${template.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    closeTemplateModal() {
        const modal = document.querySelector('.rule-template-modal');
        if (modal) {
            modal.remove();
        }
    }
    
    async importTemplate(filename) {
        try {
            const response = await fetch('/api/import-rule-template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    template_filename: filename
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.closeTemplateModal();
                this.loadProjectRules();
                alert(`Template imported successfully: ${data.imported_as}`);
            } else {
                alert(`Failed to import template: ${data.error}`);
            }
        } catch (error) {
            console.error('Error importing template:', error);
            alert('Error importing template');
        }
    }
}

// Global functions for HTML onclick
function showRuleTemplates() {
    window.rulesManager.showTemplateModal();
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.rulesManager = new RulesManager();
});