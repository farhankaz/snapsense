#!/bin/bash

# SnapSense Installation Script

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing SnapSense - Intelligent Screenshot Renaming Tool${NC}"

# Check for Python 3.6+
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    echo "Please install Python 3.6 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION < 3.6" | bc -l) )); then
    echo -e "${RED}Error: Python 3.6+ is required. Found version $PYTHON_VERSION${NC}"
    echo "Please upgrade your Python installation and try again."
    exit 1
fi

# Create installation directory
INSTALL_DIR="$HOME/.local/share/snapsense"
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "Copying application files..."
cp snapsense.py "$INSTALL_DIR/"
cp snapsense_cli.py "$INSTALL_DIR/"

# Make scripts executable
chmod +x "$INSTALL_DIR/snapsense.py"
chmod +x "$INSTALL_DIR/snapsense_cli.py"

# Create bin directory if it doesn't exist
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# Create symlink to the CLI script
SYMLINK="$BIN_DIR/snapsense"
if [ -L "$SYMLINK" ]; then
    rm "$SYMLINK"
fi
ln -s "$INSTALL_DIR/snapsense_cli.py" "$SYMLINK"
chmod +x "$SYMLINK"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}Warning: $BIN_DIR is not in your PATH.${NC}"
    echo "Add the following line to your ~/.zshrc or ~/.bash_profile:"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo "Then restart your terminal or run: source ~/.zshrc (or ~/.bash_profile)"
fi

# Install required Python packages
echo "Installing required Python packages..."
pip3 install anthropic watchdog configparser --user

# Create config directory
CONFIG_DIR="$HOME/.config/snapsense"
mkdir -p "$CONFIG_DIR"

# Create default config if it doesn't exist
CONFIG_FILE="$CONFIG_DIR/config.ini"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default configuration..."
    cat > "$CONFIG_FILE" << EOF
[General]
scan_interval = 5
scan_directory = $HOME/Desktop
screenshot_prefix = Screenshot
max_retries = 3
retry_delay = 2
EOF
fi

# Create logs directory
LOG_DIR="$HOME/Library/Logs"
mkdir -p "$LOG_DIR"

echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "To start SnapSense, run: snapsense start"
echo "To check status: snapsense status"
echo "To stop SnapSense: snapsense stop"
echo "To edit configuration: snapsense config"
echo ""
echo -e "${YELLOW}Important:${NC} Make sure your ANTHROPIC_API_KEY is set in your environment."
echo "Add this line to your ~/.zshrc file:"
echo -e "${GREEN}export ANTHROPIC_API_KEY=\"your-api-key-here\"${NC}"
echo ""
echo "Thank you for installing SnapSense!"