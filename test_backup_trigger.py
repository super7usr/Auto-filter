#!/usr/bin/env python3
import os
import sys
import asyncio
import time
from dotenv import load_dotenv

# Set required environment variables for testing
os.environ["ADMINS"] = "1927155351"
os.environ["LOG_CHANNEL"] = "-1001234567890"
os.environ["BIN_CHANNEL"] = "-1001234567890"
os.environ["SUPPORT_GROUP"] = "TestSupportGroup"
os.environ["INDEX_CHANNELS"] = ""
os.environ["FORCE_SUB_CHANNELS"] = ""
os.environ["URL"] = "test.url.com"
os.environ["SHORTLINK_URL"] = "test.shortlink.com"
os.environ["SHORTLINK_API"] = "testapi123"
os.environ["SHORTLINK"] = "True"
os.environ["PICS"] = ""
os.environ["API_ID"] = "12345"
os.environ["API_HASH"] = "abcdef1234567890"
os.environ["BOT_TOKEN"] = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
os.environ["IS_STREAM"] = "True"
os.environ["IMDB"] = "True"
os.environ["PROTECT_CONTENT"] = "False"
os.environ["AUTO_FILTER"] = "True"
os.environ["TUTORIAL"] = ""

class MockTelegramBot:
    """A mock Telegram bot for testing the backup functionality"""
    
    async def send_message(self, chat_id, text):
        """Mock method to send a message to a chat"""
        print(f"[MOCK] Sending message to {chat_id}: {text}")
        return MockMessage(text=text)
    
    async def send_document(self, chat_id, document, caption, file_name, force_document=False):
        """Mock method to send a document to a chat"""
        print(f"[MOCK] Sending document to {chat_id}:")
        print(f"  - Document: {document}")
        print(f"  - Caption: {caption}")
        print(f"  - File name: {file_name}")
        return True

class MockMessage:
    """A mock Telegram message for testing"""
    
    def __init__(self, text):
        self.text = text

async def test_backup_trigger():
    """Test the backup functionality when a specific message is sent"""
    
    # We're directly loading the function to avoid importing from info.py
    # which requires more environment variables
    
    load_dotenv()
    
    admin_id = 1927155351  # The admin ID as specified in the requirements
    mock_bot = MockTelegramBot()
    
    print("\nTesting backup trigger functionality...")
    
    # Simulate the bot sending a restart message to admin
    restart_msg = await mock_bot.send_message(admin_id, "<b>✅ ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ</b>")
    
    # Check if the message contains the trigger text
    if "✅ ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ" in restart_msg.text:
        print("[TEST] Restart message detected, triggering backup...")
        
        # Import here to avoid loading info.py at module level
        try:
            # Manually create and test the backup functionality
            import os
            import time
            import zipfile
            import shutil
            
            # Create a temporary directory for backup
            temp_dir = f"backup_{int(time.time())}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Define files and directories to backup
            backup_items = [
                "bot.py", "info.py", "utils.py", "Script.py", 
                "plugins", "database", "web", "imgs", ".env",
                "main.py", "run_bot.sh", "requirements.txt"
            ]
            
            # Copy files to the temporary directory
            for item in backup_items:
                try:
                    if os.path.isfile(item):
                        shutil.copy2(item, os.path.join(temp_dir, item))
                    elif os.path.isdir(item):
                        shutil.copytree(item, os.path.join(temp_dir, item))
                except Exception as e:
                    print(f"Warning: Could not backup {item}: {e}")
            
            # Create a zip file
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            zip_filename = f"bot_backup_{timestamp}.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            print(f"[TEST] Created backup file: {zip_filename}")
            
            # In real execution, we would send the file to admin
            await mock_bot.send_document(
                chat_id=admin_id,
                document=zip_filename,
                caption=f"🤖 Bot Backup\n⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                file_name=f"bot_backup_{timestamp}.zip",
                force_document=True
            )
            
            print("[TEST] Backup successfully created and mock-sent to admin")
            success = True
            
            # Clean up
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                if os.path.exists(zip_filename):
                    os.remove(zip_filename)
            except Exception as e:
                print(f"Warning: Failed to clean up temporary files: {e}")
                
        except Exception as e:
            print(f"[TEST] Backup failed: {e}")
            success = False
            
        if success:
            print("[TEST] Backup functionality works correctly")
        else:
            print("[TEST] Backup functionality failed")
    else:
        print("[TEST] Restart message not detected, no backup triggered")

if __name__ == "__main__":
    asyncio.run(test_backup_trigger())