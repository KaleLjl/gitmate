import argparse
from save_conversation import create_conversations_dir, save_conversation

def main():
    parser = argparse.ArgumentParser(description="SLM CLI Wrapper - Natural Language Input Tool")
    parser.add_argument("message", nargs="*", help="Natural language message to save")
    
    args = parser.parse_args()
    
    # Create conversations directory
    conversations_dir = create_conversations_dir()
    
    if args.message:
        # Join all message parts into a single string
        message = " ".join(args.message)
        filepath = save_conversation(message, conversations_dir)
        print(f"✓ Conversation saved to: {filepath}")
    
    else:
        print("SLM CLI Wrapper\nUsage:\n  python main.py \"Your natural language message here\"")
        parser.print_help()

if __name__ == "__main__":
    main()
