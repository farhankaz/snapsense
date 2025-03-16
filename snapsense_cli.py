#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main snapsense.py script
    snapsense_script = os.path.join(script_dir, "snapsense.py")
    
    # Make sure the script is executable
    if not os.access(snapsense_script, os.X_OK):
        os.chmod(snapsense_script, 0o755)
    
    # Forward all arguments to the main script
    args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
    
    # Execute the main script with the provided arguments
    subprocess.run([snapsense_script] + args)

if __name__ == "__main__":
    main()