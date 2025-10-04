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



model = lms.llm("qwen/qwen3-4b-2507")
result = model.respond("What is the meaning of life?")

print(result)

