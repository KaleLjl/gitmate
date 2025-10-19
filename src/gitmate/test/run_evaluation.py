"""Evaluation pipeline for gitmate AI responses."""
import yaml
from pathlib import Path
from gitmate.lib.service import GitMateService
from gitmate.test.report_generator import ReportGenerator


def get_test_dir():
    """Return the test directory path."""
    return Path(__file__).parent


def load_user_messages():
    """Load all user messages from user_intents.yaml."""
    test_dir = get_test_dir()
    intents_file = test_dir / "user_intents.yaml"
    
    with open(intents_file, 'r', encoding='utf-8') as f:
        messages = yaml.safe_load(f)
    
    return messages if messages else []


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
    """Load expected outputs from expected_outputs_new.yaml."""
    test_dir = get_test_dir()
    expected_file = test_dir / "expected_outputs_new.yaml"
    
    if not expected_file.exists():
        return None
    
    with open(expected_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


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


def run_evaluation():
    """Run the full evaluation pipeline."""
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
    
    # Run evaluation for all combinations
    for user_message in user_messages:
        print(f"Testing: {user_message}")
        
        for context_name, context_data in git_contexts.items():
            print(f"  - {context_name}")
            
            try:
                # Create a test service instance
                test_service = GitMateService()
                
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
                    print(f"    Running AI intent detection for: '{user_message}'")
                    ai_response = test_service.process_message(user_message)
                    print(f"    Final output: {ai_response}")
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
                
                # Record result with evaluation
                report_gen.add_result(
                    user_message=user_message,
                    git_context_name=context_name,
                    ai_response=ai_response,
                    expected_output=expected,
                    is_correct=is_correct
                )
                
            except Exception as e:
                print(f"    ERROR: {e}")
                # Record failed result
                report_gen.add_result(
                    user_message=user_message,
                    git_context_name=context_name,
                    ai_response=f"ERROR: {str(e)}",
                    expected_output=None,
                    is_correct=None
                )
    
    # Generate reports
    print("\nGenerating reports...")
    yaml_report = report_gen.generate_report(format='yaml')
    json_report = report_gen.generate_report(format='json')
    
    print(f"\nReports generated:")
    print(f"  - YAML: {yaml_report}")
    print(f"  - JSON: {json_report}")


if __name__ == "__main__":
    run_evaluation()

