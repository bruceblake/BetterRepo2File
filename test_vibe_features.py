#!/usr/bin/env python3
"""Test the Vibe Coder features in BetterRepo2File"""

import json
from pathlib import Path
from repo2file.dump_ultra import ProcessingProfile, UltraRepo2File

def test_vibe_features():
    # Create a test profile with vibe coder features
    profile = ProcessingProfile(
        name="vibe_test",
        token_budget=50000,
        model="gpt-4",
        vibe_statement="Improve checkout performance in our e-commerce platform",
        planner_output="""Based on your vibe to improve checkout performance:
1. Optimize database queries in OrderService
2. Add caching for product lookups
3. Implement async payment processing
4. Review and optimize frontend checkout flow""",
        enable_git_insights=True,
        enable_action_blocks=True,
        action_block_format='both'
    )
    
    # Create test repository path (use current directory for testing)
    repo_path = Path(".")
    output_path = Path("test_vibe_output.txt")
    
    # Process with vibe features
    processor = UltraRepo2File(profile)
    
    # Mock some action blocks for testing
    from repo2file.action_blocks import CallGraphNode, GitInsight, TodoItem
    
    # Add test action blocks
    test_todo = TodoItem(
        file="src/checkout.js",
        line=42,
        todo_type="TODO",
        text="Optimize payment processing flow",
        priority="high"
    )
    processor.action_block_generator.add_block(test_todo)
    
    test_call_graph = CallGraphNode(
        file="src/services/order_service.py",
        entity="OrderService.process_order",
        entity_type="method",
        calls=["PaymentService.process", "InventoryService.check"],
        called_by=["CheckoutController.complete"]
    )
    processor.action_block_generator.add_block(test_call_graph)
    
    print("Testing Vibe Coder features...")
    print(f"Vibe: {profile.vibe_statement}")
    print(f"Planner output: {profile.planner_output[:100]}...")
    
    # Process a small subset to test
    try:
        # Note: This will actually process your current directory - use with caution
        # For a full test, create a test repository
        print("\nGenerating output with Vibe Coder features...")
        
        # Test the header generation
        test_analysis = {
            'primary_language': 'Python',
            'frameworks': {'Flask', 'React'},
            'project_type': 'Web Application',
            'total_files': 100,
            'total_size': 500000,
            'key_files': ['src/app.py', 'src/checkout.js'],
            'recent_activity': {
                'most_changed': [('src/payment.py', 15), ('src/cart.js', 12)],
                'recent_files': [('src/api.py', 'john_doe', '2024-01-20')]
            }
        }
        
        # Generate Gemini Planner Primer
        gemini_section = processor._generate_gemini_planner_primer(test_analysis, repo_path)
        print("\n=== GEMINI PLANNER PRIMER ===")
        print('\n'.join(gemini_section[:20]))  # Print first 20 lines
        
        # Generate Claude Coder Context header
        claude_section = processor._generate_claude_coder_context_header()
        print("\n=== CLAUDE CODER CONTEXT ===")
        print('\n'.join(claude_section[:20]))  # Print first 20 lines
        
        # Test textual anchors
        test_content = """def process_payment(order_id):
    # Process payment for order
    order = get_order(order_id)
    return payment_gateway.charge(order.total)"""
        
        test_entities = [
            type('Entity', (), {
                'qualified_name': 'process_payment',
                'type': 'function',
                'line_start': 1,
                'line_end': 4
            })
        ]
        
        anchored_content = processor.processor._add_entity_anchors(test_content, test_entities)
        print("\n=== ANCHORED CONTENT ===")
        print(anchored_content)
        
        print("\nVibe Coder feature test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vibe_features()