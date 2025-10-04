import argparse
import yaml
from datetime import datetime
from pathlib import Path

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

def main():
    parser = argparse.ArgumentParser(description="SLM CLI Wrapper - Natural Language Input Tool")
    parser.add_argument("message", nargs="*", help="Natural language message to save")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    # Create conversations directory
    conversations_dir = create_conversations_dir()
    
    if args.interactive:
        print("SLM CLI Wrapper - Interactive Mode")
        print("Type your natural language input (or 'quit' to exit):")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input:
                    filepath = save_conversation(user_input, conversations_dir)
                    print(f"✓ Conversation saved to: {filepath}")
                else:
                    print("Please enter a message.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
    
    elif args.message:
        # Join all message parts into a single string
        message = " ".join(args.message)
        filepath = save_conversation(message, conversations_dir)
        print(f"✓ Conversation saved to: {filepath}")
    
    else:
        print("SLM CLI Wrapper")
        print("Usage:")
        print("  python main.py \"Your natural language message here\"")
        print("  python main.py -i  # Interactive mode")
        parser.print_help()

if __name__ == "__main__":
    main()