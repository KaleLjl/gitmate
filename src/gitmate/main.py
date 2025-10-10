import argparse
from pathlib import Path
# Import the probes to get the current git status
from gitmate.git_probes import get_git_context
# Import system paths from config
from gitmate.system_config import PROMPTS_DIR
# Import model and conversation management functions
from gitmate.anwser import (
    create_conversations_dir,
    save_conversation,
    update_conversation_with_ai_response,
    get_ai_response
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
    
    # Prepare git context
    git_context_str = get_git_context()

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
    
    # Get AI response
    result = get_ai_response(message, git_context_str, system_prompt)
    
    print(result)

    # Update the conversation file with AI response
    if update_conversation_with_ai_response(filepath, result):
        return
    else:
        print("Failed to save AI response")
    

if __name__ == "__main__":
    main()
