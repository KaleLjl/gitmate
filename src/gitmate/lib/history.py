from datetime import datetime
import yaml
from gitmate.config import DATA_ROOT, CONVERSATIONS_DIR


def create_conversations_dir():
    """Create conversations directory if it doesn't exist"""
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    return CONVERSATIONS_DIR


def generate_filename():
    """Generate a unique filename based on current timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"conversation_{timestamp}.yaml"


def save_conversation(message):
    """Save the conversation message to a YAML file"""
    # Create conversations directory if it doesn't exist
    conversations_dir = create_conversations_dir()
    
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
