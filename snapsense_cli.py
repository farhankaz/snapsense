#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import time

def is_process_running(pid):
    """Check if a process with the given PID is running and is a SnapSense process."""
    try:
        # Send signal 0 to check if process exists
        os.kill(pid, 0)
        
        # On macOS, we can check the process name to verify it's SnapSense
        try:
            # Use ps command to get process name
            result = subprocess.run(['ps', '-p', str(pid), '-o', 'comm='], 
                                   capture_output=True, text=True, check=False)
            process_name = result.stdout.strip()
            
            # Check if it's a python process
            if 'python' in process_name.lower():
                # Further verify by checking if it's running our script
                result = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], 
                                       capture_output=True, text=True, check=False)
                command = result.stdout.strip()
                return 'snapsense.py' in command or 'snapsense_cli.py' in command
            return False
        except (subprocess.SubprocessError, FileNotFoundError):
            # If we can't check the process name, just assume it's running
            return True
    except OSError:
        return False

def read_pid_file():
    """Read the process ID from the file with proper error handling."""
    pid_file = os.path.expanduser("~/.config/snapsense/snapsense.pid")
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid_str = f.read().strip()
                if pid_str.isdigit():
                    return int(pid_str)
        except (IOError, ValueError):
            pass
    return None

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
    
    # If the action is 'start', check if already running before starting
    if args and args[0] == 'start':
        pid = read_pid_file()
        if pid and is_process_running(pid):
            print(f"SnapSense is already running (PID: {pid})")
            sys.exit(0)
    
    # Execute the main script with the provided arguments
    subprocess.run([snapsense_script] + args)

if __name__ == "__main__":
    main()