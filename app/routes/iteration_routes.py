"""
Iteration Routes Blueprint for BetterRepo2File v2.0
Handles iteration workflow endpoints
"""
from flask import Blueprint, request, jsonify, Response, current_app
import json
import os

iteration_bp = Blueprint('iteration', __name__, url_prefix='/api')


@iteration_bp.route('/iterations/history')
def iteration_history():
    """Get iteration history"""
    try:
        # Get iteration history from session or storage
        session_manager = current_app.session_manager
        
        # For now, return empty history
        return jsonify({
            'iterations': [],
            'total': 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@iteration_bp.route('/logs/stream')
def log_stream():
    """Stream logs via Server-Sent Events"""
    def generate():
        # This would typically connect to a log source
        # For now, just send heartbeats
        while True:
            yield f"data: {json.dumps({'type': 'heartbeat', 'message': 'Log stream active'})}\n\n"
            import time
            time.sleep(5)
    
    return Response(generate(), content_type='text/event-stream')


@iteration_bp.route('/refine_prompt_v2', methods=['POST'])
def refine_prompt_v2():
    """Refine a user's feature description using AI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        repo_url = data.get('repo_url')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
            
        # Import the LLM augmenter
        from repo2file.llm_augmenter import LLMAugmenter
        
        # Check if API key is available in environment
        has_gemini_key = bool(os.getenv('GEMINI_API_KEY'))
        has_google_key = bool(os.getenv('GOOGLE_API_KEY'))
        
        print(f"Checking API keys - GEMINI_API_KEY: {has_gemini_key}, GOOGLE_API_KEY: {has_google_key}")
        
        if not has_gemini_key and not has_google_key:
            print("No API keys found, using fallback")
            # Provide a helpful enhancement without AI
            repo_name = repo_url.split('/')[-1].replace('.git', '') if repo_url else 'current repository'
            return jsonify({
                'success': True,
                'refined_prompt': f"Enhanced Feature Description:\n\n{prompt}\n\nImplementation Details:\n- Repository: {repo_name}\n- Focus on clean, maintainable code\n- Include comprehensive tests\n- Consider edge cases and error handling\n- Document any API changes"
            })
        
        try:
            # Create augmenter instance (it will use env vars)
            augmenter = LLMAugmenter(
                provider="gemini",
                api_key_env_var="GOOGLE_API_KEY" if has_google_key else "GEMINI_API_KEY"
            )
            
            # Check if the augmenter is available
            if not augmenter.is_available():
                print("LLM augmenter not available")
                raise Exception("LLM provider not available")
            
            # Create a simple repo context if URL provided
            repo_context = ""
            if repo_url:
                repo_name = repo_url.split('/')[-1].replace('.git', '')
                repo_context = f"Repository: {repo_name}"
            
            # Refine the prompt
            print(f"Attempting to refine prompt: {prompt[:100]}...")
            refined = augmenter.refine_user_prompt(prompt, repo_context)
            print(f"Successfully refined prompt")
            
            return jsonify({
                'success': True,
                'refined_prompt': refined
            })
            
        except Exception as llm_error:
            print(f"LLM error: {llm_error}")
            # Fallback response
            return jsonify({
                'success': True,
                'refined_prompt': f"Feature Request:\n{prompt}\n\nPlease implement with clean code and comprehensive tests."
            })
            
    except Exception as e:
        print(f"Error in refine_prompt_v2: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500