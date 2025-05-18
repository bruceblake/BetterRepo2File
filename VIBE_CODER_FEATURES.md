# Vibe Coder Features - BetterRepo2File

This document describes the new "Vibe Coder" features added to BetterRepo2File that enhance the workflow between Gemini 1.5 Pro Preview (for planning) and Claude Code (for implementation).

## Overview

The Vibe Coder features transform BetterRepo2File into a sophisticated bridge between AI planning and AI coding systems, making it easy for developers to:

1. **Articulate their high-level goals** ("vibes") and get them formatted for planning AI
2. **Integrate plans from Gemini** into rich context for Claude Code
3. **Navigate code with textual anchors** for precise AI instructions
4. **Prepare iteration feedback** for continuous improvement cycles

## Feature 1: Vibe & Goal Input with Gemini Planner Primer

### UI Components
- **Vibe Statement Input**: A text area where you describe your high-level goal
- **Location**: Ultra Mode settings in the web interface

### CLI Parameters
```bash
python dump_ultra.py ./myrepo output.txt --vibe "Improve checkout speed" --planner "plan.txt"
```

### Generated Output Section
The tool generates a special section at the top of the output file:

```
==================================================
SECTION 1: FOR AI PLANNING AGENT (e.g., Gemini 1.5 Pro in AI Studio)
Copy and paste this section into your Planning AI.
==================================================

MY VIBE / PRIMARY GOAL:
[Your vibe statement here]

PROJECT SNAPSHOT & HIGH-LEVEL CONTEXT:
- Primary Language: Python
- Key Frameworks/Libraries: Flask, React, PostgreSQL
- Core Modules/Areas:
  - /app: Main application logic
  - /api: REST API endpoints
  - /frontend: React UI components

AREAS OF RECENT ACTIVITY / POTENTIAL CHURN (Git Insights):
- Files with most changes (last 30d): payment.py (15 commits), cart.js (12 commits)
- Key files recently modified: api.py (john_doe, 2024-01-20)

SUMMARY OF KNOWN TODOS / ACTION ITEMS (Top 5-10):
- [TODO from checkout.js]: Optimize payment processing flow
- [FIXME from database.py]: Add connection pooling
```

## Feature 2: Claude Coder Super-Context Generation

### Planner Output Integration
After receiving a plan from Gemini, you can:
1. Paste it into the "AI Planner Output" field in the UI
2. Use the `--planner` CLI argument with a file path or direct text

### Generated Output Section
```
==================================================
SECTION 2: FOR AI CODING AGENT (e.g., Local Claude Code)
This section contains the detailed codebase context and the plan from the AI Planning Agent.
==================================================

PLAN/INSTRUCTIONS FROM AI PLANNING AGENT (Gemini 1.5 Pro):
[Your pasted Gemini plan here]

--- DETAILED CODEBASE CONTEXT ---

[Full hierarchical manifest with code, insights, and anchors]
```

### Textual Anchors System
The output includes navigation anchors for precise code references:

#### File Anchors
```
[[FILE_START: src/services/payment.py]]
File: src/services/payment.py
Language: Python
Size: 2,450 bytes | Tokens: 512
----------------------------------------
```

#### Function/Method/Class Anchors
```python
[[FUNCTION_START: process_payment]]
def process_payment(order_id):
    # Process payment for order
    order = get_order(order_id)
    return payment_gateway.charge(order.total)
[[FUNCTION_END: process_payment]]
```

### Usage Example with Claude
You can now give precise instructions like:
> "Claude, modify the function marked [[FUNCTION_START: process_payment]] in [[FILE_START: src/services/payment.py]] based on step 3 of the plan."

## Feature 3: Smart Iteration Package Builder (Coming Soon)

This feature will help you compile feedback for the next planning cycle:

### Inputs
1. Current (modified) project directory
2. Previous Repo2File output
3. Your feedback file containing:
   - Claude's logs
   - Test results
   - Your observations

### Generated Output
```
==================================================
ITERATION UPDATE & REQUEST FOR NEXT PLAN (For Gemini 1.5 Pro Planner)
==================================================

ORIGINAL VIBE / PRIMARY GOAL:
[From previous cycle]

PREVIOUS PLAN FROM GEMINI:
[Extracted from previous output]

USER SUMMARY & CLAUDE'S EXECUTION FEEDBACK:
[Your feedback content]

KEY CHANGES MADE TO CODEBASE:
- Diff Summary: 5 files changed, 120 insertions(+), 30 deletions(-)
- Key Modified Files:
  - src/payment.py: Added async processing
  - tests/test_payment.py: New tests added

CURRENT RELEVANT CODE CONTEXT:
[Focused snapshot of modified areas]

REQUEST FOR NEXT PLANNING STEPS:
Based on the above, please advise on the next steps...
```

## Feature 4: Enhanced UI/UX for Vibe Coders

### Textual Anchors
- All code entities are marked with `[[TYPE_START: name]]` and `[[TYPE_END: name]]` tags
- Types include: `FILE`, `FUNCTION`, `METHOD`, `CLASS`
- Makes it easy to reference specific code locations

### Quick Copy Snippets (Coming Soon)
- Copy buttons next to key items in the UI output
- One-click copy of anchors like `[[FILE_START: app/utils.py]]`
- Reduces manual typing when crafting prompts

### Configurable Verbosity
- Control how much detail appears in different sections
- Options for inline vs. manifest-only insights
- Customize based on your workflow needs

## Configuration Options

### ProcessingProfile Fields
```python
# Vibe Coder specific fields
vibe_statement: str = ''  # Your high-level goal
planner_output: str = ''  # AI planner's output to integrate
enable_action_blocks: bool = True  # Enable structured blocks
action_block_format: str = 'both'  # 'inline', 'manifest', or 'both'
```

### UI Settings
All vibe coder features are available in Ultra Mode:
1. Enable Ultra Mode
2. Fill in the Vibe Statement field
3. Optionally paste Planner Output
4. Configure other settings as needed
5. Generate your enhanced context

## Best Practices

1. **Clear Vibe Statements**: Be specific about your goals
   - Good: "Improve checkout performance by 50%"
   - Better: "Optimize database queries and add caching to reduce checkout page load time"

2. **Structured Plans**: When pasting Gemini's output, ensure it has clear steps
3. **Use Anchors**: Reference specific code locations in your prompts to both AIs
4. **Iterate Frequently**: Use the iteration package builder for continuous improvement

## Example Workflow

1. **Start with a Vibe**:
   ```
   "Improve the performance of our checkout process"
   ```

2. **Generate Planner Context**:
   - Run Repo2File with `--vibe` parameter
   - Copy Section 1 to Gemini in AI Studio

3. **Get Plan from Gemini**:
   - Receive structured plan with specific steps
   - Copy the plan output

4. **Generate Coder Context**:
   - Run Repo2File again with both `--vibe` and `--planner`
   - Copy Section 2 to Claude Code

5. **Execute with Claude**:
   - Reference specific anchors in your prompts
   - Let Claude implement the changes

6. **Iterate** (Coming Soon):
   - Test the changes
   - Prepare feedback package
   - Return to step 2 for next cycle

## Technical Implementation

### Action Blocks
The system uses structured action blocks for machine-readable insights:
- `CALL_GRAPH_NODE`: Function relationships
- `GIT_INSIGHT`: Version control information
- `TODO_ITEM`: Existing code tasks
- `PCA_NOTE`: Proactive context augmentation
- `CODE_QUALITY_METRIC`: Objective quality measures

### Performance Optimizations
- Intelligent token budget allocation between sections
- Cached processing for repeated operations
- Parallel analysis where possible

## Future Enhancements

1. **Interactive Manifest Explorer**: HTML view of the codebase structure
2. **AI Provider Integrations**: Direct API calls to Gemini/Claude
3. **Workflow Templates**: Pre-configured patterns for common tasks
4. **Collaborative Features**: Team-based vibe sharing and planning

## Conclusion

The Vibe Coder features in BetterRepo2File create a seamless bridge between high-level planning with Gemini and detailed implementation with Claude Code. By providing structured context, textual anchors, and iteration support, it significantly enhances the AI-assisted development workflow.