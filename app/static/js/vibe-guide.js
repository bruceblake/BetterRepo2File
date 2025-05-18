// Vibe Guide JavaScript
class VibeGuide {
    constructor() {
        this.tips = [];
        this.pinnedTips = JSON.parse(localStorage.getItem('pinnedTips') || '[]');
        this.currentStage = null;
        this.init();
    }
    
    async init() {
        await this.loadTips();
        this.renderTips();
        this.attachEventListeners();
    }
    
    async loadTips() {
        try {
            const response = await fetch('/static/json/vibe_guide_tips.json');
            this.tips = await response.json();
        } catch (error) {
            console.error('Failed to load vibe guide tips:', error);
        }
    }
    
    renderTips() {
        const container = document.getElementById('tipsContainer');
        if (!container) return;
        
        // Sort tips: pinned first, then by category
        const sortedTips = [...this.tips].sort((a, b) => {
            const aPinned = this.pinnedTips.includes(a.id);
            const bPinned = this.pinnedTips.includes(b.id);
            
            if (aPinned && !bPinned) return -1;
            if (!aPinned && bPinned) return 1;
            
            // If both pinned or both not pinned, sort by category
            return a.category.localeCompare(b.category);
        });
        
        // Group tips by category
        const grouped = {};
        sortedTips.forEach(tip => {
            if (!grouped[tip.category]) {
                grouped[tip.category] = [];
            }
            grouped[tip.category].push(tip);
        });
        
        // Render tips
        container.innerHTML = '';
        Object.entries(grouped).forEach(([category, tips]) => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'tip-category';
            categoryDiv.innerHTML = `<h4>${this.formatCategory(category)}</h4>`;
            
            tips.forEach(tip => {
                const tipElement = this.createTipElement(tip);
                categoryDiv.appendChild(tipElement);
            });
            
            container.appendChild(categoryDiv);
        });
    }
    
    createTipElement(tip) {
        const isPinned = this.pinnedTips.includes(tip.id);
        const isHighlighted = this.shouldHighlight(tip);
        
        const tipDiv = document.createElement('div');
        tipDiv.className = `tip ${isPinned ? 'pinned' : ''} ${isHighlighted ? 'highlighted' : ''}`;
        tipDiv.dataset.tipId = tip.id;
        
        tipDiv.innerHTML = `
            <div class="tip-header">
                <h5>${tip.title}</h5>
                <div class="tip-actions">
                    <button class="pin-btn" title="${isPinned ? 'Unpin' : 'Pin'} tip">
                        <span class="material-symbols-outlined">${isPinned ? 'push_pin' : 'keep'}</span>
                    </button>
                    <button class="apply-btn" title="Apply as rule">
                        <span class="material-symbols-outlined">add_circle</span>
                    </button>
                </div>
            </div>
            <div class="tip-content">
                <p>${this.parseMarkdown(tip.content)}</p>
                ${tip.external_link ? `<a href="${tip.external_link}" target="_blank" rel="noopener noreferrer">Learn more →</a>` : ''}
            </div>
        `;
        
        return tipDiv;
    }
    
    formatCategory(category) {
        const formatted = category.replace(/_/g, ' ');
        return formatted.charAt(0).toUpperCase() + formatted.slice(1);
    }
    
    parseMarkdown(text) {
        // Basic markdown parsing
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
    
    shouldHighlight(tip) {
        if (!this.currentStage) return false;
        
        const stageMapping = {
            'planning': ['planning'],
            'coding': ['coding_setup'],
            'iteration': ['iteration_feedback']
        };
        
        const relevantCategories = stageMapping[this.currentStage] || [];
        return relevantCategories.includes(tip.category);
    }
    
    attachEventListeners() {
        // Pin/unpin buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.pin-btn')) {
                const tipDiv = e.target.closest('.tip');
                const tipId = tipDiv.dataset.tipId;
                this.togglePin(tipId);
            }
            
            if (e.target.closest('.apply-btn')) {
                const tipDiv = e.target.closest('.tip');
                const tipId = tipDiv.dataset.tipId;
                this.applyAsRule(tipId);
            }
        });
        
        // Listen for stage changes
        document.addEventListener('vibeStageChanged', (e) => {
            this.currentStage = e.detail.stage;
            this.updateHighlights();
        });
    }
    
    togglePin(tipId) {
        const index = this.pinnedTips.indexOf(tipId);
        if (index > -1) {
            this.pinnedTips.splice(index, 1);
        } else {
            this.pinnedTips.push(tipId);
        }
        
        localStorage.setItem('pinnedTips', JSON.stringify(this.pinnedTips));
        this.renderTips();
    }
    
    applyAsRule(tipId) {
        const tip = this.tips.find(t => t.id === tipId);
        if (!tip) return;
        
        // Determine where to apply the rule based on current UI state
        const vibeTextarea = document.getElementById('featureVibe');
        const plannerTextarea = document.querySelector('textarea[placeholder*="planner"]');
        
        let targetElement = null;
        let message = '';
        
        if (this.currentStage === 'planning' && vibeTextarea) {
            targetElement = vibeTextarea;
            message = 'Added to feature vibe';
        } else if (this.currentStage === 'coding' && plannerTextarea) {
            targetElement = plannerTextarea;
            message = 'Added to planner instructions';
        }
        
        if (targetElement) {
            const currentValue = targetElement.value;
            const separator = currentValue ? '\n\n' : '';
            targetElement.value = currentValue + separator + `[VIBE GUIDE TIP - ${tip.title}]\n${tip.content}`;
            
            // Show confirmation
            this.showNotification(message);
        }
        
        // Also append to ai_guardrails.md if it exists
        this.appendToGuardrails(tip);
    }
    
    async appendToGuardrails(tip) {
        // This would need backend API to append to ai_guardrails.md
        // For now, just log
        console.log('Would append to ai_guardrails.md:', tip);
    }
    
    updateHighlights() {
        document.querySelectorAll('.tip').forEach(tipDiv => {
            const tipId = tipDiv.dataset.tipId;
            const tip = this.tips.find(t => t.id === tipId);
            if (tip && this.shouldHighlight(tip)) {
                tipDiv.classList.add('highlighted');
            } else {
                tipDiv.classList.remove('highlighted');
            }
        });
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'vibe-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
}

// Global functions for HTML onclick
function toggleVibeGuide() {
    const drawer = document.getElementById('vibeGuideDrawer');
    drawer.classList.toggle('open');
    
    // Initialize Vibe Guide on first open
    if (!window.vibeGuide && drawer.classList.contains('open')) {
        window.vibeGuide = new VibeGuide();
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    // Auto-initialize if drawer is already visible
    const drawer = document.getElementById('vibeGuideDrawer');
    if (drawer && drawer.classList.contains('open')) {
        window.vibeGuide = new VibeGuide();
    }
});