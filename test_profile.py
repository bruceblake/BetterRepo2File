#!/usr/bin/env python
import sys
sys.path.append('.')

# Test loading the profile
try:
    from app.profiles import DEFAULT_PROFILES
    gemini_profile = DEFAULT_PROFILES['gemini']
    print(f"Gemini profile loaded successfully:")
    print(f"  Model: {gemini_profile.model}")
    print(f"  Token budget: {gemini_profile.token_budget}")
    print(f"  Truncation strategy: {getattr(gemini_profile, 'truncation_strategy', 'default')}")
    print(f"  Generate manifest: {getattr(gemini_profile, 'generate_manifest', False)}")
except Exception as e:
    print(f"Error loading profile: {e}")
    import traceback
    traceback.print_exc()