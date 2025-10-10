import argparse
from pathlib import Path
# Import the probes to get the current git status
from gitmate.git_probes import get_git_context
# Import system paths from config
from gitmate.system_config import PROMPT_PATH
# Import model and conversation management functions
from gitmate.anwser import (
    create_conversations_dir,
    save_conversation,
    update_conversation_with_ai_response,
    get_ai_response
)
    
def main():
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

    # Read system prompt 
    try:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        system_prompt = ""

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
