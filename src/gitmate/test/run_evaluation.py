"""Evaluation pipeline for gitmate AI responses."""
import yaml
from pathlib import Path
from gitmate.anwser import get_ai_response
from gitmate.system_config import PROMPTS_DIR
from gitmate.test.report_generator import ReportGenerator


def get_test_dir():
    """Return the test directory path."""
    return Path(__file__).parent


def load_user_intents():
    """Load all user intents from user_intents.yaml."""
    test_dir = get_test_dir()
    intents_file = test_dir / "user_intents.yaml"
    
    with open(intents_file, 'r', encoding='utf-8') as f:
        intents = yaml.safe_load(f)
    
    return intents if intents else []


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
    
    # Load system prompt (using context-aware prompt)
    prompt_path = PROMPTS_DIR / "context_aware_prompt.md"
    
    try:
        system_prompt = prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: System prompt not found at {prompt_path}")
        return
    
    # Load test data
    user_intents = load_user_intents()
    git_contexts = load_git_contexts()
    
    print(f"Loaded {len(user_intents)} user intents")
    print(f"Loaded {len(git_contexts)} git contexts")
    print(f"Running {len(user_intents) * len(git_contexts)} test combinations...\n")
    
    # Initialize report generator
    report_gen = ReportGenerator(reports_dir)
    
    # Run evaluation for all combinations
    for user_intent in user_intents:
        print(f"Testing: {user_intent}")
        
        for context_name, context_data in git_contexts.items():
            print(f"  - {context_name}")
            
            # Format git context as YAML string
            git_context_str = format_git_context(context_data)
            
            try:
                # Get AI response
                ai_response = get_ai_response(
                    message=user_intent,
                    git_context_str=git_context_str,
                    system_prompt=system_prompt
                )
                
                # Record result
                report_gen.add_result(
                    user_intent=user_intent,
                    git_context_name=context_name,
                    ai_response=ai_response
                )
                
            except Exception as e:
                print(f"    ERROR: {e}")
                # Record failed result
                report_gen.add_result(
                    user_intent=user_intent,
                    git_context_name=context_name,
                    ai_response=f"ERROR: {str(e)}"
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

