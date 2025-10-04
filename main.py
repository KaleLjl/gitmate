# load and save conversation to YAML file
import yaml
from datetime import datetime
from pathlib import Path
## Import LM Studio
import lmstudio as lms

def create_conversations_dir():
    """Create conversations directory if it doesn't exist"""
    conversations_dir = Path("conversations")
    conversations_dir.mkdir(exist_ok=True)
    return conversations_dir

def generate_filename():
    """Generate a unique filename based on current timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"conversation_{timestamp}.yaml"

def save_conversation(message, conversations_dir):
    """Save the conversation message to a YAML file"""
    conversation_data = {
        "timestamp": datetime.now().isoformat(),
        "user_input": message,
        "metadata": {
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "user_message"
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


# model = lms.llm("qwen/qwen3-4b-2507")
# result = model.respond("What is the meaning of life?")

# print(result)

def main():
    # model = lms.llm("qwen/qwen3-4b-2507")
    # user_input = "What is the meaning of life?"
    # result = model.respond(user_input)
    # print(f"Model response: {result}")
    conversations_dir = create_conversations_dir()
    latest_message = load_latest_conversation(conversations_dir)
    
    if latest_message:
        print(f"Latest message: {latest_message}")
    else:
        print("No conversations found.")


if __name__ == "__main__":
    main()