def main():
    """Main entry point"""
    try:
        print(f"Arguments: {sys.argv}")
        if len(sys.argv) < 3:
            print("Usage: python dump_ultra.py <repo_path> <output_file> [profile_file] [options]")
            print("\nOptions:")
            print("  --model MODEL      LLM model to optimize for (default: gpt-4)")
            print("  --budget TOKENS    Token budget (default: 500000)")
            print("  --profile NAME     Use named profile")
            print("  --exclude PATTERN  Add exclusion pattern")
            print("  --boost PATTERN    Boost priority for files matching pattern")
            print("  --manifest         Generate hierarchical manifest")
            print("  --truncation MODE  Truncation strategy (semantic, basic, middle_summarize, business_logic)")
            print("\nExamples:")
            print("  python dump_ultra.py ./myrepo output.txt")
            print("  python dump_ultra.py ./myrepo output.txt --model claude-3 --budget 200000")
            print("  python dump_ultra.py ./myrepo output.txt --exclude '*.log' --boost '*.py:0.5'")
            sys.exit(1)
        
        repo_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])
        
        # Parse arguments
        profile = ProcessingProfile(
            name="default",
            token_budget=DEFAULT_TOKEN_BUDGET,
            model="gpt-4"
        )
        
        # Process profile first
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--profile' and i + 1 < len(sys.argv):
                profile_name = sys.argv[i + 1]
                print(f"Loading profile: {profile_name}")
                # Load from app/profiles.py
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from app.profiles import DEFAULT_PROFILES
                if profile_name in DEFAULT_PROFILES:
                    app_profile = DEFAULT_PROFILES[profile_name]
                    # Convert app profile to dump_ultra profile
                    print(f"Profile model: {app_profile.model}")
                    profile = ProcessingProfile(
                        name=app_profile.name,
                        token_budget=app_profile.token_budget,
                        model=app_profile.model,
                        exclude_patterns=app_profile.exclude_patterns,
                        generate_manifest=getattr(app_profile, 'generate_manifest', True),
                        truncation_strategy=getattr(app_profile, 'truncation_strategy', 'semantic')
                    )
                    # Copy priority patterns if they exist
                    if hasattr(app_profile, 'priority_patterns'):
                        for pattern, score in app_profile.priority_patterns.items():
                            profile.priority_boost[pattern] = score
                else:
                    # Try loading as a file path for backwards compatibility
                    profile_path = Path(profile_name)
                    if profile_path.exists():
                        profile = ProcessingProfile.load(profile_path)
                i += 2
            else:
                i += 1
        
        # Then process other arguments (which may override profile settings)
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--model' and i + 1 < len(sys.argv):
                model_arg = sys.argv[i + 1]
                print(f"Setting model from arg: '{model_arg}'")
                if model_arg:  # Only set if not empty
                    profile.model = model_arg
                i += 2
            elif arg == '--budget' and i + 1 < len(sys.argv):
                profile.token_budget = int(sys.argv[i + 1])
                i += 2
            elif arg == '--exclude' and i + 1 < len(sys.argv):
                profile.exclude_patterns.append(sys.argv[i + 1])
                i += 2
            elif arg == '--boost' and i + 1 < len(sys.argv):
                pattern, boost = sys.argv[i + 1].split(':')
                profile.priority_boost[pattern] = float(boost)
                i += 2
            elif arg == '--profile':
                # Skip - already processed in first pass
                i += 2
            elif arg == '--manifest':
                profile.generate_manifest = True
                i += 1
            elif arg == '--truncation' and i + 1 < len(sys.argv):
                profile.truncation_strategy = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        # Process repository
        processor = UltraRepo2File(profile)
        processor.process_repository(repo_path, output_path)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)