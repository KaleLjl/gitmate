"""Evaluation pipeline for gitmate AI responses."""
import argparse
import yaml
from pathlib import Path
from gitmate.lib.service import GitMateService
from gitmate.test.report_generator import ReportGenerator


def get_test_dir():
    """Return the test directory path."""
    return Path(__file__).parent


def load_user_messages():
    """Load all user messages from centralized intent definitions."""
    from gitmate.lib.intent_utils import get_all_examples
    return get_all_examples()


def load_git_contexts():
    """Load all git contexts from git_contexts/ directory."""
    test_dir = get_test_dir()
    contexts = {}
    contexts_dir = test_dir / "git_contexts"
    
    for context_file in sorted(contexts_dir.glob("*.yaml")):
        context_name = context_file.stem
        with open(context_file, 'r', encoding='utf-8') as f:
            context_data = yaml.safe_load(f)
            contexts[context_name] = context_data
    
    return contexts


def load_expected_outputs():
    """Load expected outputs from intent_definitions.yaml (new structure)."""
    from gitmate.lib.intent_utils import get_intent_expected_outputs, get_intent_mapping
    
    # Get intent mapping and expected outputs
    intent_mapping = get_intent_mapping()
    intent_names = list(intent_mapping.values())
    
    # Build expected outputs structure for backward compatibility
    expected_outputs = {}
    for intent_name in set(intent_names):
        intent_outputs = get_intent_expected_outputs(intent_name)
        if intent_outputs:
            # Find a message that maps to this intent
            for message, mapped_intent in intent_mapping.items():
                if mapped_intent == intent_name:
                    expected_outputs[message] = intent_outputs
                    break
    
    return expected_outputs if expected_outputs else None


def normalize_output(text):
    """Normalize output for fair comparison by removing code blocks and whitespace."""
    if not text:
        return ""
    
    # Remove code block markers
    text = text.strip()
    text = text.replace('```bash\n', '').replace('```bash', '')
    text = text.replace('```\n', '').replace('```', '')
    
    # Normalize whitespace and line breaks
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    return text.strip()


def format_git_context(context_dict):
    """Format git context dict as YAML string."""
    return yaml.dump(
        context_dict,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    ).strip()


def list_available_intents():
    """Display all available intents and their example messages."""
    from gitmate.lib.intent_utils import load_intents
    
    intents = load_intents()
    print("Available intents for testing:")
    print("=" * 50)
    
    for intent_name, intent_data in intents['intents'].items():
        description = intent_data.get('description', 'No description')
        examples = intent_data.get('examples', [])
        
        print(f"\n{intent_name.upper()}")
        print(f"  Description: {description}")
        print(f"  Example messages: {', '.join(examples)}")
    
    print(f"\nTotal intents: {len(intents['intents'])}")
    print("\nUsage examples:")
    print("  python -m gitmate.test.run_evaluation --intent commit")
    print("  python -m gitmate.test.run_evaluation --intent commit --intent push")
    print("  python -m gitmate.test.run_evaluation  # Run all intents")


def run_evaluation(filter_intents=None):
    """Run the full evaluation pipeline.
    
    Args:
        filter_intents: List of intent names to test. If None, test all intents.
    """
    test_dir = get_test_dir()
    reports_dir = test_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Load test data
    user_messages = load_user_messages()
    git_contexts = load_git_contexts()
    expected_outputs = load_expected_outputs()
    
    print(f"Loaded {len(user_messages)} user messages")
    print(f"Loaded {len(git_contexts)} git contexts")
    if expected_outputs:
        print("Loaded expected outputs for evaluation")
    print(f"Running {len(user_messages) * len(git_contexts)} test combinations...")
    print("Testing complete pipeline: AI Intent Detection → Post-Processor → Git Command\n")
    
    # Initialize report generator
    report_gen = ReportGenerator(reports_dir)
    
    # Group messages by intent for better organization
    from gitmate.lib.intent_utils import get_intent_mapping
    intent_mapping = get_intent_mapping()
    
    # Create intent groups
    intent_groups = {}
    for message in user_messages:
        intent = intent_mapping.get(message, 'unknown')
        if intent not in intent_groups:
            intent_groups[intent] = []
        intent_groups[intent].append(message)
    
    # Filter intents if specified
    if filter_intents:
        # Validate intent names
        from gitmate.lib.intent_utils import get_intent_names
        valid_intents = get_intent_names()
        invalid_intents = [intent for intent in filter_intents if intent not in valid_intents]
        if invalid_intents:
            print(f"Warning: Invalid intent names: {', '.join(invalid_intents)}")
            print(f"Valid intents: {', '.join(valid_intents)}")
        
        # Filter intent groups
        filtered_groups = {intent: messages for intent, messages in intent_groups.items() 
                          if intent in filter_intents}
        intent_groups = filtered_groups
        
        print(f"Filtering to test only: {', '.join(intent_groups.keys())}")
        print(f"Total test combinations: {sum(len(messages) * len(git_contexts) for messages in intent_groups.values())}")
    
    # Run evaluation organized by intent
    for intent, messages in intent_groups.items():
        print(f"\n{'='*60}")
        print(f"TESTING INTENT: {intent.upper()}")
        print(f"Messages: {', '.join(messages)}")
        print(f"{'='*60}")
        
        for user_message in messages:
            print(f"\n  Testing message: '{user_message}'")
            # Create a test service instance
            test_service = GitMateService()
            for context_name, context_data in git_contexts.items():
                print(f"    - Context: {context_name}")
                
                try:
                    # For testing, we only mock the git context, not the AI response
                    # This allows us to test the complete pipeline: AI intent detection + post-processing
                    import gitmate.lib.service as service_module
                    original_get_git_context = service_module.get_git_context
                    
                    def mock_get_git_context():
                        return format_git_context(context_data)
                    
                    # Replace only the git context function temporarily
                    service_module.get_git_context = mock_get_git_context
                    
                    try:
                        # Get AI response using the test service (with real AI intent detection)
                        ai_response = test_service.process_message(user_message)
                        print(f"      AI Response: {ai_response}")
                    finally:
                        # Restore the original function
                        service_module.get_git_context = original_get_git_context
                    
                    # Get expected output if available
                    expected = None
                    is_correct = None
                    if expected_outputs and user_message in expected_outputs:
                        if context_name in expected_outputs[user_message]:
                            expected_data = expected_outputs[user_message][context_name]
                            expected = expected_data.get('output', '')
                            
                            # Compare normalized outputs
                            is_correct = (
                                normalize_output(ai_response) == 
                                normalize_output(expected)
                            )
                            status = "✓ PASS" if is_correct else "✗ FAIL"
                            print(f"      Expected: {expected}")
                            print(f"      Result: {status}")
                    
                    # Record result with evaluation
                    report_gen.add_result(
                        user_message=user_message,
                        git_context_name=context_name,
                        ai_response=ai_response,
                        expected_output=expected,
                        is_correct=is_correct
                    )
                    
                except Exception as e:
                    print(f"      ERROR: {e}")
                    # Record failed result
                    report_gen.add_result(
                        user_message=user_message,
                        git_context_name=context_name,
                        ai_response=f"ERROR: {str(e)}",
                        expected_output=None,
                        is_correct=None
                    )
    
    # Generate reports with new organization
    print("\n" + "="*60)
    print("GENERATING REPORTS")
    print("="*60)
    yaml_report = report_gen.generate_report(format='yaml', organize_by_intent=True)
    json_report = report_gen.generate_report(format='json', organize_by_intent=True)
    
    print(f"\nReports generated with intent-based organization:")
    print(f"  - YAML: {yaml_report}")
    print(f"  - JSON: {json_report}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run GitMate evaluation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Run all intents
  %(prog)s --intent commit           # Test only commit intent
  %(prog)s --intent commit push     # Test commit and push intents
  %(prog)s --list-intents           # List available intents
        """
    )
    
    parser.add_argument(
        '--intent',
        action='append',
        help='Intent to test (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--list-intents',
        action='store_true',
        help='List all available intents and exit'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Handle list intents
    if args.list_intents:
        list_available_intents()
        exit(0)
    
    # Run evaluation with optional intent filtering
    filter_intents = args.intent if args.intent else None
    run_evaluation(filter_intents=filter_intents)

