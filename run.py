import os
import sys
import time
import datetime

# Print the start message
print(f"Starting Telegram bot at {datetime.datetime.now()}")

# Run the main script
if __name__ == "__main__":
    try:
        import main
        main.run_bot()
    except Exception as e:
        import traceback
        print(f"Error starting bot: {e}")
        traceback.print_exc()