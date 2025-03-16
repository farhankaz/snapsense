#!/bin/bash

# SnapSense Uninstallation Script

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Uninstalling SnapSense - Intelligent Screenshot Renaming Tool${NC}"

# First, stop the service if it's running
echo "Stopping SnapSense service if running..."
~/.local/bin/snapsense stop 2>/dev/null

# Remove application files
echo "Removing application files..."
rm -rf "$HOME/.local/share/snapsense"

# Remove symlink
echo "Removing command symlink..."
rm -f "$HOME/.local/bin/snapsense"

# Ask if user wants to remove configuration and logs
read -p "Do you want to remove configuration and log files? (y/n): " REMOVE_CONFIG
if [[ $REMOVE_CONFIG == "y" || $REMOVE_CONFIG == "Y" ]]; then
    echo "Removing configuration files..."
    rm -rf "$HOME/.config/snapsense"
    
    echo "Removing log files..."
    rm -f "$HOME/Library/Logs/snapsense.log"
else
    echo "Keeping configuration and log files."
    echo "Configuration remains at: $HOME/.config/snapsense"
    echo "Log file remains at: $HOME/Library/Logs/snapsense.log"
fi

echo -e "${GREEN}SnapSense has been uninstalled.${NC}"
echo "Thank you for using SnapSense!"