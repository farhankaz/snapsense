#!/usr/bin/env python3
"""
Test script for SnapSense

This script tests the SnapSense application by creating a test screenshot
and verifying that it gets processed correctly.
"""

import os
import sys
import time
import shutil
import subprocess
import argparse
from pathlib import Path

def create_test_image(directory, prefix="Screenshot"):
    """Create a test image in the specified directory."""
    # Find a sample image to copy
    sample_images = [
        "/System/Library/Desktop Pictures/Solid Colors/Solid Aqua.png",
        "/Library/Desktop Pictures/Solid Colors/Solid Aqua.png",
        "/System/Library/Desktop Pictures/Mojave.heic",
        "/Library/Desktop Pictures/Mojave.heic"
    ]
    
    sample_image = None
    for img in sample_images:
        if os.path.exists(img):
            sample_image = img
            break
    
    if not sample_image:
        print("Error: Could not find a sample image to use for testing.")
        return None
    
    # Create a test image
    timestamp = int(time.time())
    test_image = os.path.join(directory, f"{prefix} {timestamp}.png")
    
    try:
        shutil.copy(sample_image, test_image)
        print(f"Created test image: {test_image}")
        return test_image
    except Exception as e:
        print(f"Error creating test image: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Test SnapSense functionality")
    parser.add_argument('--config', action='store_true', help='Use directory from config file')
    parser.add_argument('--dir', type=str, help='Directory to create test image in')
    parser.add_argument('--prefix', type=str, default="Screenshot", help='Prefix for test image')
    
    args = parser.parse_args()
    
    # Determine the directory to use
    if args.config:
        # Read from config file
        config_path = os.path.expanduser("~/.config/snapsense/config.ini")
        if not os.path.exists(config_path):
            print("Error: Config file not found. Run 'snapsense config' first.")
            return 1
        
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        
        directory = os.path.expanduser(config["General"]["scan_directory"])
        prefix = config["General"]["screenshot_prefix"]
    else:
        directory = args.dir or os.path.expanduser("~/Desktop")
        prefix = args.prefix
    
    # Ensure the directory exists
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return 1
    
    # Check if SnapSense is running
    try:
        result = subprocess.run(["snapsense", "status"], 
                               capture_output=True, text=True)
        if "not running" in result.stdout:
            print("Warning: SnapSense is not running. Start it with 'snapsense start'.")
            response = input("Do you want to start SnapSense now? (y/n): ")
            if response.lower() == 'y':
                subprocess.run(["snapsense", "start"])
                print("Waiting for SnapSense to initialize...")
                time.sleep(3)
            else:
                print("Test will continue, but the image won't be processed until SnapSense is started.")
    except Exception as e:
        print(f"Warning: Could not check SnapSense status: {str(e)}")
    
    # Create a test image
    test_image = create_test_image(directory, prefix)
    if not test_image:
        return 1
    
    print("\nTest image created successfully!")
    print(f"Location: {test_image}")
    print("\nIf SnapSense is running, it should process this image shortly.")
    print("Check the logs at ~/Library/Logs/snapsense.log for details.")
    
    # Wait and check if the file was renamed
    print("\nWaiting 10 seconds to see if the file gets renamed...")
    time.sleep(10)
    
    if os.path.exists(test_image):
        print("The test image has not been renamed yet.")
        print("This could be because:")
        print("1. SnapSense is not running")
        print("2. The scan interval hasn't elapsed yet")
        print("3. There was an error processing the image")
        print("\nCheck the logs for more information.")
    else:
        print("The test image has been renamed! SnapSense is working correctly.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())