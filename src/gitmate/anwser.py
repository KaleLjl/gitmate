from datetime import datetime
import yaml
from mlx_lm import load, generate
from gitmate.config import (
    DATA_ROOT, CONVERSATIONS_DIR, MLX_MODEL
)


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


def get_mlx_ai_response(message: str, git_context_str: str, system_prompt: str) -> str:
    """
    Get AI response using the local MLX model.
    
    Args:
        message: The user's natural language input
        git_context_str: The git repository context as a YAML string
        system_prompt: The system prompt for the model
    
    Returns:
        The AI-generated response as a string
    """
    # Load the model
    model, tokenizer = load(MLX_MODEL)

    # Apply the prompt 
    prompt = (
        "User message: " + message
        + "\n\n---\n\nGit Context (YAML):\n```yaml\n"
        + git_context_str
        + "\n```\n\nEnd of context."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True  # This tells the model the following needs to be assistant message 
    )

    result = generate(model, tokenizer, prompt=prompt, verbose=False)

    # Post-process: normalize output (commit message + URL placeholders)
    try:
        from gitmate.postprocess import normalize_output, enforce_policies
        result = normalize_output(result)
        # Enforce deterministic, context-aware planners; returns a single code block
        result = enforce_policies(message, git_context_str, result)
    except Exception:
        # If post-processing fails for any reason, return normalized or raw result
        pass
    
    return result

