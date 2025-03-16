#!/usr/bin/env python3
import os
import time
import sys
import json
import argparse
import logging
import signal
import anthropic
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser("~/Library/Logs/snapsense.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SnapSense")

# Default configuration
DEFAULT_CONFIG = {
    "General": {
        "scan_interval": "5",  # seconds
        "scan_directory": os.path.expanduser("~/Desktop"),
        "screenshot_prefix": "Screenshot",
        "max_retries": "3",
        "retry_delay": "2"  # seconds
    }
}

CONFIG_PATH = os.path.expanduser("~/.config/snapsense/config.ini")

def ensure_config_exists():
    """Ensure the config file exists, create with defaults if it doesn't."""
    config_dir = os.path.dirname(CONFIG_PATH)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    if not os.path.exists(CONFIG_PATH):
        config = configparser.ConfigParser()
        config.read_dict(DEFAULT_CONFIG)
        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
        logger.info(f"Created default configuration at {CONFIG_PATH}")
    
    return load_config()

def load_config():
    """Load configuration from the config file."""
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not set")
            sys.exit(1)
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.screenshot_prefix = self.config["General"]["screenshot_prefix"]
        self.max_retries = int(self.config["General"]["max_retries"])
        self.retry_delay = int(self.config["General"]["retry_delay"])
        
        # Image file extensions to process
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        
        logger.info(f"ScreenshotHandler initialized with prefix: {self.screenshot_prefix}")
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        self.process_file(event.src_path)
    
    def process_file(self, file_path):
        """Process a newly created file if it matches our criteria."""
        path = Path(file_path)
        
        # Check if it's an image file
        if path.suffix.lower() not in self.image_extensions:
            return
        
        # Check if it starts with the screenshot prefix
        if not path.stem.startswith(self.screenshot_prefix):
            return
        
        logger.info(f"Processing new screenshot: {file_path}")
        
        # Give the file system a moment to finish writing the file
        time.sleep(0.5)
        
        # Generate a new filename using Claude
        for attempt in range(self.max_retries):
            try:
                new_name = self.generate_filename(file_path)
                if new_name:
                    self.rename_file(file_path, new_name)
                    break
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
    
    def generate_filename(self, image_path):
        """Use Claude to generate an appropriate filename for the image."""
        logger.info(f"Generating filename for {image_path}")
        
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            message = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=100,
                temperature=0.2,
                system="You are an AI assistant that generates concise, descriptive filenames for images. Create filenames that are clear, specific, and under 50 characters. Use lowercase with hyphens between words. Don't include file extensions.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": anthropic.utils.encode_base64(image_data)
                                }
                            },
                            {
                                "type": "text",
                                "text": "Generate a concise, descriptive filename for this image. The filename should be clear, specific, and under 50 characters. Use lowercase with hyphens between words. Don't include file extensions."
                            }
                        ]
                    }
                ]
            )
            
            # Extract the suggested filename
            suggested_name = message.content[0].text.strip()
            
            # Clean up the filename (remove quotes, periods, etc.)
            clean_name = re.sub(r'[^\w\-]', '', suggested_name.replace(' ', '-')).lower()
            
            # Ensure it's not empty
            if not clean_name:
                clean_name = "unnamed-image"
            
            logger.info(f"Generated filename: {clean_name}")
            return clean_name
            
        except Exception as e:
            logger.error(f"Error generating filename: {str(e)}")
            return None
    
    def rename_file(self, old_path, new_name):
        """Rename the file with the generated name."""
        path = Path(old_path)
        new_path = path.parent / f"{new_name}{path.suffix}"
        
        # If the new path already exists, add a number to make it unique
        counter = 1
        while new_path.exists():
            new_path = path.parent / f"{new_name}-{counter}{path.suffix}"
            counter += 1
        
        try:
            os.rename(old_path, new_path)
            logger.info(f"Renamed: {old_path} -> {new_path}")
        except Exception as e:
            logger.error(f"Error renaming file: {str(e)}")

def scan_directory(config):
    """Scan the directory for existing screenshots."""
    directory = config["General"]["scan_directory"]
    handler = ScreenshotHandler(config)
    
    logger.info(f"Scanning directory: {directory}")
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                handler.process_file(file_path)
    except Exception as e:
        logger.error(f"Error scanning directory: {str(e)}")

def start_monitoring(config):
    """Start monitoring the directory for new screenshots."""
    directory = config["General"]["scan_directory"]
    scan_interval = int(config["General"]["scan_interval"])
    
    logger.info(f"Starting monitoring of {directory} (interval: {scan_interval}s)")
    
    event_handler = ScreenshotHandler(config)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    
    try:
        while True:
            # Periodically scan the directory for any missed files
            scan_directory(config)
            time.sleep(scan_interval)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def write_pid_file(pid):
    """Write the process ID to a file."""
    pid_dir = os.path.expanduser("~/.config/snapsense")
    if not os.path.exists(pid_dir):
        os.makedirs(pid_dir)
    
    pid_file = os.path.join(pid_dir, "snapsense.pid")
    with open(pid_file, 'w') as f:
        f.write(str(pid))
    
    return pid_file

def read_pid_file():
    """Read the process ID from the file."""
    pid_file = os.path.expanduser("~/.config/snapsense/snapsense.pid")
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            return int(f.read().strip())
    return None

def is_process_running(pid):
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def main():
    parser = argparse.ArgumentParser(description="SnapSense - Intelligent Screenshot Renaming")
    parser.add_argument('action', choices=['start', 'stop', 'status', 'config'], 
                        help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        # Check if already running
        pid = read_pid_file()
        if pid and is_process_running(pid):
            print(f"SnapSense is already running (PID: {pid})")
            return
        
        # Load configuration
        config = ensure_config_exists()
        
        # Fork the process to run in the background
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                print(f"SnapSense started with PID: {pid}")
                write_pid_file(pid)
                sys.exit(0)
        except OSError as e:
            logger.error(f"Fork failed: {e}")
            sys.exit(1)
        
        # Child process continues here
        # Detach from terminal
        os.setsid()
        os.umask(0)
        
        # Close all file descriptors
        for fd in range(3, 1024):
            try:
                os.close(fd)
            except OSError:
                pass
        
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        with open(os.devnull, 'r') as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        
        log_file = os.path.expanduser("~/Library/Logs/snapsense.log")
        with open(log_file, 'a+') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())
        
        # Start monitoring
        start_monitoring(config)
    
    elif args.action == 'stop':
        pid = read_pid_file()
        if pid and is_process_running(pid):
            print(f"Stopping SnapSense (PID: {pid})...")
            try:
                os.kill(pid, signal.SIGTERM)
                # Wait for the process to terminate
                for _ in range(10):
                    if not is_process_running(pid):
                        break
                    time.sleep(0.5)
                else:
                    # Force kill if it doesn't terminate
                    os.kill(pid, signal.SIGKILL)
                
                print("SnapSense stopped")
                # Remove PID file
                os.remove(os.path.expanduser("~/.config/snapsense/snapsense.pid"))
            except OSError as e:
                print(f"Error stopping SnapSense: {e}")
        else:
            print("SnapSense is not running")
    
    elif args.action == 'status':
        pid = read_pid_file()
        if pid and is_process_running(pid):
            print(f"SnapSense is running (PID: {pid})")
            
            # Show configuration
            config = load_config()
            print("\nCurrent configuration:")
            print(f"  Scan directory: {config['General']['scan_directory']}")
            print(f"  Scan interval: {config['General']['scan_interval']} seconds")
            print(f"  Screenshot prefix: {config['General']['screenshot_prefix']}")
        else:
            print("SnapSense is not running")
    
    elif args.action == 'config':
        # Open the config file in the default editor
        config_path = ensure_config_exists()
        editor = os.environ.get('EDITOR', 'nano')
        os.system(f"{editor} {CONFIG_PATH}")

if __name__ == "__main__":
    main()