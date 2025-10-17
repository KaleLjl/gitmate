import argparse
from pathlib import Path
# Import the probes to get the current git status
from gitmate.git_probes import get_git_context
# Import system paths from config
from gitmate.config import PROMPTS_DIR
# Import user configuration loader
from gitmate.config import load_or_create_user_config
# Import model and conversation management functions
from gitmate.anwser import (
    create_conversations_dir,
    save_conversation,
    update_conversation_with_ai_response,
    get_mlx_ai_response,
    get_transformers_ai_response
)

def get_prompt_path(prompt_filename):
    """Get the full path for a prompt file."""
    return PROMPTS_DIR / prompt_filename
    
def main():
    # Configurable prompt selection - change this to select different prompts
    SELECTED_PROMPT = "general_prompt.md"
    
    # Setup the CLI
    parser = argparse.ArgumentParser(description="A Local LLM wrapper for using git")
    parser.add_argument('message', nargs='*', help='Natural Language for git action')
    args = parser.parse_args()
    
    # Check if message is provided
    if not args.message:
        print("Please provide a message.")
        return
    
    # Store the message value
    message = ' '.join(args.message)
    
    # Load user configuration
    config = load_or_create_user_config()
    
    # Conditionally prepare git context based on user configuration
    if config.get('git_context', True):
        git_context_str = get_git_context()
        SELECTED_PROMPT = "context_aware_prompt.md"
    else:
        git_context_str = ""

    # Read system prompt with validation
    prompt_path = get_prompt_path(SELECTED_PROMPT)
    try:
        system_prompt = prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: Prompt file '{SELECTED_PROMPT}' not found")
        print("\nAvailable prompts:")
        if PROMPTS_DIR.exists():
            for prompt_file in sorted(PROMPTS_DIR.glob("*.md")):
                print(f"  - {prompt_file.name}")
        return

    # Create conversations directory and save user message
    conversations_dir = create_conversations_dir()
    filepath = save_conversation(message, conversations_dir)
    
    # Get AI response based on selected inference engine
    engine = config.get('inference_engine', 'mlx')
    if engine == 'transformers':
        result = get_transformers_ai_response(message, git_context_str, system_prompt)
    else:
        result = get_mlx_ai_response(message, git_context_str, system_prompt)
    
    print(result)

    # Update the conversation file with AI response
    if update_conversation_with_ai_response(filepath, result):
        return
    else:
        print("Failed to save AI response")
    

if __name__ == "__main__":
    main()
