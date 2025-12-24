#!/usr/bin/env python3
"""
Keep-alive script for the Flask CRM application.
Monitors the app and restarts it if it crashes.
"""
import subprocess
import time
import sys
import os

def main():
    """Monitor and restart the Flask app if it crashes."""
    print("Starting CRM keep-alive monitor...")

    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    while True:
        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Flask app...")
            # Run the Flask app
            process = subprocess.Popen([sys.executable, 'app.py'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True,
                                     bufsize=1,
                                     universal_newlines=True)

            # Print output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            return_code = process.poll()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Flask app exited with code {return_code}")

            if return_code == 0:
                print("Flask app exited normally. Exiting monitor.")
                break
            else:
                print("Flask app crashed. Restarting in 5 seconds...")
                time.sleep(5)

        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt. Stopping monitor.")
            break
        except Exception as e:
            print(f"Error in monitor: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    main()

















