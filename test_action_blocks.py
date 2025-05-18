#!/usr/bin/env python3
"""Test AI Action Blocks implementation"""

from repo2file.action_blocks import (
    ActionBlockGenerator, CallGraphNode, GitInsight, 
    TodoItem, PCANote, CodeQualityMetric
)

def test_action_blocks():
    # Create a generator with all features enabled
    config = {
        'enable_action_blocks': True,
        'action_block_format': 'both',
        'action_block_types': ['CALL_GRAPH_NODE', 'GIT_INSIGHT', 'TODO_ITEM', 'PCA_NOTE', 'CODE_QUALITY_METRIC'],
        'action_block_filters': {
            'min_complexity': 10,
            'min_priority': 'medium',
            'include_private_methods': False
        }
    }
    
    generator = ActionBlockGenerator(config)
    
    # Add a Git insight
    git_block = GitInsight(
        file="src/main.py",
        last_mod_date="2024-01-15",
        last_mod_author="jane.doe",
        last_commit="Added error handling",
        commit_hash="abc123d",
        change_frequency_90d=12,
        recent_contributors=["jane.doe", "john.smith"]
    )
    generator.add_block(git_block)
    
    # Add a TODO item
    todo_block = TodoItem(
        file="src/auth.py",
        line=45,
        todo_type="FIXME",
        text="Security vulnerability in token validation",
        priority="high"
    )
    generator.add_block(todo_block)
    
    # Add a call graph node
    call_block = CallGraphNode(
        file="src/api.py",
        entity="APIHandler.handle_request",
        entity_type="method",
        calls=["validate_token", "process_data", "send_response"],
        called_by=["main", "test_api_handler"]
    )
    generator.add_block(call_block)
    
    # Add a code quality metric
    quality_block = CodeQualityMetric(
        file="src/database.py",
        entity="DatabaseManager.execute_query",
        metric="cyclomatic_complexity",
        value=25,
        threshold=10,
        severity="error"
    )
    generator.add_block(quality_block)
    
    # Generate inline blocks for a specific file
    inline_blocks = generator.generate_inline_blocks("src/api.py")
    print("Inline blocks for src/api.py:")
    for block in inline_blocks:
        print(block)
    print()
    
    # Generate manifest section
    manifest_section = generator.generate_manifest_section()
    print("Manifest section:")
    print(manifest_section)
    print()
    
    # Generate structured output
    structured = generator.generate_structured_output()
    print("Structured output:")
    import json
    print(json.dumps(structured, indent=2))

if __name__ == "__main__":
    test_action_blocks()