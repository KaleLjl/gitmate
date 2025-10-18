"""
Interactive REPL mode for GitMate.
"""
from gitmate.lib.service import GitMateService


def main():
    """Run the interactive REPL mode."""
    print("GitMate Interactive Mode")
    print("Type your git-related questions. Type 'exit' or 'quit' to stop.")
    print("=" * 50)
    
    # Initialize service once at startup
    try:
        service = GitMateService()
        print("GitMate service initialized successfully.")
    except Exception as e:
        print(f"Error initializing GitMate service: {e}")
        return
    
    # REPL loop
    while True:
        try:
            # Get user input
            user_input = input("\n> ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Process the message
            try:
                result = service.process_message(user_input)
                print(f"\n{result}")
            except Exception as e:
                print(f"Error processing message: {e}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
