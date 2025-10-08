import argparse
from datetime import datetime
from pathlib import Path
import yaml
# import the probes to get the current git status
from gitmate.git_probes import save_repo_description
#import the inference engine
from mlx_lm import load, generate

PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path.home() / ".gitmate"
CONVERSATIONS_DIR = DATA_ROOT / "conversations"
PROMPT_PATH = PACKAGE_ROOT / "prompts" / "context_aware_prompt.md"
DEFAULT_REPO_STATUS_PATH = DATA_ROOT / "repo_status.yaml"
MODEL_PATH = PACKAGE_ROOT / "models" / "Qwen3-4B-Instruct-2507-MLX-4bit"

def create_conversations_dir():
    """Create conversations directory if it doesn't exist"""
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    return CONVERSATIONS_DIR

def generate_filename():
    """Generate a unique filename based on current timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"conversation_{timestamp}.yaml"

def save_conversation(message, conversations_dir):
    """Save the conversation message to a YAML file"""
    conversation_data = {
        "user_input": message,
        "metadata": {
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    filename = generate_filename()
    filepath = conversations_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(conversation_data, file, default_flow_style=False, allow_unicode=True)
    
    return filepath

def load_latest_conversation(conversations_dir):
    """Load the user message from the latest conversation file"""
    if not conversations_dir.exists():
        return None
    
    # Get all YAML files in the conversations directory
    yaml_files = list(conversations_dir.glob("conversation_*.yaml"))
    
    if not yaml_files:
        return None
    
    # Sort files by modification time (most recent first)
    latest_file = max(yaml_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as file:
            conversation_data = yaml.safe_load(file)
            return conversation_data.get('user_input')
    except (yaml.YAMLError, FileNotFoundError, KeyError):
        return None
    
def update_conversation_with_ai_response(filepath, ai_response):
    """Update only AI_response and metadata.updated_at in the YAML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            conversation_data = yaml.safe_load(file) or {}

        # Update updated_at
        metadata = conversation_data.get('metadata') or {}
        metadata['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversation_data['metadata'] = metadata

        # Preserve order and append AI_response last
        new_data = {}
        for k, v in conversation_data.items():
            if isinstance(k, str) and k.lower() == 'ai_response':
                continue
            new_data[k] = v
        new_data['AI_response'] = str(ai_response)

        with open(filepath, 'w', encoding='utf-8') as file:
            yaml.dump(new_data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return True
    except Exception as e:
        print(f"Error updating conversation file: {e}")
        return False
    
def main():
    # Setup the CLI
    parser = argparse.ArgumentParser(description="A Local LLM wrapper for using git")
    parser.add_argument('message', nargs='*', help='Natural Language for git action')
    args = parser.parse_args()
    
    # Create conversations directory first
    conversations_dir = create_conversations_dir()
    
    # Check if message is provided
    if not args.message:
        print("Please provide a message.")
        return
    
    # Store and save the message value
    message = ' '.join(args.message)
    filepath = save_conversation(message, conversations_dir)
    
    # Read system prompt 
    try:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        system_prompt = ""

    # Read the git context file 
    save_repo_description(repo_path=Path.cwd(), output_path=DEFAULT_REPO_STATUS_PATH)
    with open(DEFAULT_REPO_STATUS_PATH, "r", encoding="utf-8") as f:
        git_context = yaml.safe_load(f) or {}
    git_context_str = yaml.dump(git_context, default_flow_style=False, allow_unicode=True, sort_keys=False).strip() or "No git context available."

    
    # Load the model
    model, tokenizer = load(MODEL_PATH)

    # apply the prompt 
    prompt= "User message: " + message + "\n\n---\n\nContext:\n```yaml\n" + git_context_str      # define the input prompt

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt= True  # This add_generation_prompt tells the model , the following need to be assitant message 
    )

    result = generate(model,tokenizer,prompt=prompt,verbose = False)



    print(result)

    # Update the conversation file with AI response
    if update_conversation_with_ai_response(filepath, result):
        return
    else:
        print("Failed to save AI response")
    

if __name__ == "__main__":
    main()
