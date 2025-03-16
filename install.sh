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

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Warning: 'uv' is not installed.${NC}"
    echo "Please install 'uv' using: brew install uv"
    echo "Then run this script again."
    exit 1
fi

# Check Python version using Python itself for accurate version comparison
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_VERSION_CHECK=$(python3 -c 'import sys; print(sys.version_info >= (3, 6))')

if [ "$PYTHON_VERSION_CHECK" != "True" ]; then
    echo -e "${RED}Error: Python 3.6+ is required. Found version $PYTHON_VERSION${NC}"
    echo "Please upgrade your Python installation and try again."
    exit 1
fi

# Create installation directory
INSTALL_DIR="$HOME/.local/share/snapsense"
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "Copying application files..."
if ! cp snapsense.py "$INSTALL_DIR/" || ! cp snapsense_cli.py "$INSTALL_DIR/"; then
    echo -e "${RED}Error: Failed to copy application files.${NC}"
    exit 1
fi

# Make scripts executable
if ! chmod +x "$INSTALL_DIR/snapsense.py" || ! chmod +x "$INSTALL_DIR/snapsense_cli.py"; then
    echo -e "${RED}Error: Failed to make scripts executable.${NC}"
    exit 1
fi

# Create bin directory if it doesn't exist
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# Create symlink to the wrapper script
SYMLINK="$BIN_DIR/snapsense"
if [ -L "$SYMLINK" ]; then
    rm "$SYMLINK"
fi
if ! ln -s "$INSTALL_DIR/snapsense_wrapper.sh" "$SYMLINK"; then
    echo -e "${RED}Error: Failed to create symlink.${NC}"
    exit 1
fi
if ! chmod +x "$SYMLINK"; then
    echo -e "${RED}Error: Failed to make symlink executable.${NC}"
    exit 1
fi

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}Warning: $BIN_DIR is not in your PATH.${NC}"
    echo "Add the following line to your ~/.zshrc or ~/.bash_profile:"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo "Then restart your terminal or run: source ~/.zshrc (or ~/.bash_profile)"
fi

# Create virtual environment using uv with Python 3.12
echo "Creating virtual environment with Python 3.12..."
VENV_DIR="$INSTALL_DIR/venv"
if ! uv venv --python 3.12 "$VENV_DIR"; then
    echo -e "${RED}Error: Failed to create virtual environment with Python 3.12.${NC}"
    exit 1
fi

# Install required Python packages into the virtual environment
echo "Installing required Python packages..."
# First activate the virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    # Save current directory
    CURRENT_DIR=$(pwd)
    # Source the activation script in a subshell to avoid changing the current shell's state
    if ! (source "$VENV_DIR/bin/activate" && cd "$CURRENT_DIR" && uv pip install anthropic watchdog configparser); then
        echo -e "${RED}Error: Failed to install required packages.${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Virtual environment activation script not found.${NC}"
    exit 1
fi

# Create a wrapper script for snapsense_cli.py that activates the virtual environment
echo "Creating wrapper script..."
WRAPPER_SCRIPT="$INSTALL_DIR/snapsense_wrapper.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Wrapper script to run snapsense_cli.py in the virtual environment

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hardcode the installation directory path instead of trying to derive it
INSTALL_DIR="$HOME/.local/share/snapsense"
VENV_DIR="\$INSTALL_DIR/venv"
CLI_SCRIPT="\$INSTALL_DIR/snapsense_cli.py"

# Debug information
echo "Installation directory: \$INSTALL_DIR"
echo "Virtual environment path: \$VENV_DIR"
echo "CLI script path: \$CLI_SCRIPT"

# Check if virtual environment exists
if [ ! -d "\$VENV_DIR" ]; then
    echo -e "\${RED}Error: Virtual environment directory not found at \$VENV_DIR\${NC}"
    echo "Please reinstall SnapSense."
    exit 1
fi

# Check for Python interpreter (could be a file or symlink)
if [ ! -e "\$VENV_DIR/bin/python" ]; then
    echo -e "\${RED}Error: Python interpreter not found in virtual environment at \$VENV_DIR/bin/python\${NC}"
    echo "Please reinstall SnapSense."
    exit 1
fi

# Use a subshell to activate the virtual environment and run the CLI script
(source "\$VENV_DIR/bin/activate" && python "\$CLI_SCRIPT" "\$@")
EOF

# Make the wrapper script executable
if ! chmod +x "$WRAPPER_SCRIPT"; then
    echo -e "${RED}Error: Failed to make wrapper script executable.${NC}"
    exit 1
fi

# Create config directory
CONFIG_DIR="$HOME/.config/snapsense"
mkdir -p "$CONFIG_DIR"

# Create default config if it doesn't exist
CONFIG_FILE="$CONFIG_DIR/config.ini"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default configuration..."
    cat > "$CONFIG_FILE" << EOF
[General]
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