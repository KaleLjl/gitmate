import argparse
from lib.save_conversation import create_conversations_dir, save_conversation
from lib.connect_with_SLM import LMStudioConnector
from lib.load_conversation import get_latest_user_message

def main():
    parser = argparse.ArgumentParser(description="SLM CLI Wrapper - Natural Language Input Tool")
    parser.add_argument("message", nargs="*", help="Natural language message to save")
    parser.add_argument("--process", "-p", action="store_true", help="Process latest saved conversation with SLM")
    
    args = parser.parse_args()
    
    # Create conversations directory
    conversations_dir = create_conversations_dir()
    
    if args.process:
        # Process the latest conversation with SLM
        try:
            connector = LMStudioConnector()
            print("🔄 Processing latest conversation with SLM...")
            
            response = connector.process_latest_conversation(conversations_dir)
            if response:
                print(f"🤖 SLM Response: {response}")
                print("✓ Response saved to conversation file")
            else:
                print("❌ No conversations found to process")
                
        except ConnectionError as e:
            print(f"❌ Connection Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif args.message:
        # Join all message parts into a single string
        message = " ".join(args.message)
        filepath = save_conversation(message, conversations_dir)
        print(f"✓ Conversation saved to: {filepath}")
        
        # Ask if user wants to process with SLM
        process_now = input("\n🤖 Process this message with SLM now? (y/N): ").strip().lower()
        if process_now in ['y', 'yes']:
            try:
                connector = LMStudioConnector()
                print("🔄 Processing with SLM...")
                response = connector.send_message(message)
                print(f"🤖 SLM Response: {response}")
                
                # Update the saved conversation with response
                from lib.load_conversation import update_conversation_with_response
                update_conversation_with_response(filepath, response)
                print("✓ Response saved to conversation file")
                
            except ConnectionError as e:
                print(f"❌ Connection Error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    else:
        print("SLM CLI Wrapper")
        print("Usage:")
        print("  python main.py \"Your natural language message here\"")
        print("  python main.py --process    # Process latest saved conversation")
        parser.print_help()

if __name__ == "__main__":
    main()
