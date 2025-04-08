#!/usr/bin/env python3
import os
import sys
import asyncio
from dotenv import load_dotenv

async def create_backup_and_send(admin_id):
    """Create a backup of the code and send it to the specified admin ID."""
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
        "plugins", "database", "web", "imgs", ".env"
    ]
    
    # Copy files to the temporary directory
    for item in backup_items:
        if os.path.isfile(item):
            shutil.copy2(item, os.path.join(temp_dir, item))
        elif os.path.isdir(item):
            shutil.copytree(item, os.path.join(temp_dir, item))
    
    # Create a zip file
    zip_filename = f"bot_backup_{int(time.time())}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # In a real scenario, this would send the backup to the admin
    # Since we can't send it via Telegram in this test, we'll just print a message
    print(f"[TEST] Backup created: {zip_filename}")
    print(f"[TEST] In production, this would be sent to admin ID: {admin_id}")
    
    # Clean up
    shutil.rmtree(temp_dir)
    # Keep the zip file for now so we can verify it works
    # os.remove(zip_filename)
    
    return zip_filename

async def main():
    load_dotenv()
    
    admin_id = 1927155351  # The admin ID as specified in the requirements
    
    print("Testing backup functionality...")
    zip_filename = await create_backup_and_send(admin_id)
    
    # Verify zip file contents
    import zipfile
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        print(f"\nContents of {zip_filename}:")
        for item in zipf.namelist():
            print(f" - {item}")

if __name__ == "__main__":
    asyncio.run(main())