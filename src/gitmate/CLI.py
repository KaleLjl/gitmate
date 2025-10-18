import argparse
from gitmate.lib.service import GitMateService

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
    
    # Initialize service and process message
    try:
        service = GitMateService()
        result = service.process_message(message)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        return
    

if __name__ == "__main__":
    main()
