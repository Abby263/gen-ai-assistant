import requests
import time
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

def print_separator():
    print("\n" + "="*50 + "\n")

def pretty_print_json(data):
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def get_updates():
    """Get all updates from the bot"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    return response.json()

def display_updates():
    """Display updates in a structured format"""
    print_separator()
    print("🔍 CHECKING BOT UPDATES")
    print_separator()
    
    updates = get_updates()
    if updates.get('ok'):
        messages = updates.get('result', [])
        if not messages:
            print("No messages found")
            return None
        
        print(f"Found {len(messages)} messages:")
        for idx, update in enumerate(messages, 1):
            message = update.get('message', {})
            print(f"\nMessage #{idx}:")
            print(f"├── Update ID: {update.get('update_id')}")
            print(f"├── From: {message.get('from', {}).get('first_name', 'Unknown')}")
            print(f"├── Chat ID: {message.get('chat', {}).get('id', 'Unknown')}")
            print(f"├── Time: {datetime.fromtimestamp(message.get('date', 0))}")
            print(f"└── Text: {message.get('text', 'No text')}")
        
        return messages
    else:
        print("❌ Error getting updates:")
        pretty_print_json(updates)
        return None

def send_test_message(chat_id):
    """Send a test message and display the result"""
    print_separator()
    print("📤 SENDING TEST MESSAGE")
    print_separator()
    
    test_message = f"Test message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"Sending to chat_id: {chat_id}")
    print(f"Message: {test_message}")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": test_message
    })
    
    result = response.json()
    if result.get('ok'):
        print("\n✅ Message sent successfully!")
        print("\nResponse details:")
        pretty_print_json(result)
    else:
        print("\n❌ Failed to send message:")
        pretty_print_json(result)

def verify_bot():
    """Verify bot token and permissions"""
    print_separator()
    print("🔍 VERIFYING BOT SETUP")
    print_separator()
    
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    response = requests.get(url)
    result = response.json()
    
    if result.get('ok'):
        bot_info = result['result']
        print("✅ Bot verification successful!")
        print(f"Bot username: @{bot_info['username']}")
        print(f"Bot name: {bot_info['first_name']}")
        return True
    else:
        print("❌ Bot verification failed!")
        print("Error:", result.get('description', 'Unknown error'))
        return False

def main_menu():
    """Interactive testing menu"""
    while True:
        print_separator()
        print("🤖 TELEGRAM BOT TESTER")
        print_separator()
        print("1. Check for messages")
        print("2. Send test message")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            messages = display_updates()
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            messages = display_updates()
            if messages:
                chat_id = messages[0]['message']['chat']['id']
                send_test_message(chat_id)
            else:
                print("\n❌ No chat_id found. Please send a message to the bot first.")
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            print("\nGoodbye! 👋")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    if not verify_bot():
        print("\n❌ Please check your bot token and try again.")
        exit(1)
    main_menu()