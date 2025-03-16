#!/bin/bash

# SnapSense Packaging Script
# This script creates a distributable package of SnapSense

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating SnapSense distribution package${NC}"

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/snapsense"
mkdir -p "$PACKAGE_DIR"

# Copy all necessary files
echo "Copying files to package directory..."
cp snapsense.py "$PACKAGE_DIR/"
cp snapsense_cli.py "$PACKAGE_DIR/"
cp install.sh "$PACKAGE_DIR/"
cp uninstall.sh "$PACKAGE_DIR/"
cp README.md "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"
cp test_snapsense.py "$PACKAGE_DIR/"

# Create the distribution archive
DIST_DIR="./dist"
mkdir -p "$DIST_DIR"
VERSION=$(date +"%Y%m%d")
ARCHIVE_NAME="snapsense-$VERSION.tar.gz"
ARCHIVE_PATH="$DIST_DIR/$ARCHIVE_NAME"

echo "Creating distribution archive..."
tar -czf "$ARCHIVE_PATH" -C "$TEMP_DIR" snapsense

# Clean up
rm -rf "$TEMP_DIR"

echo -e "${GREEN}Package created successfully!${NC}"
echo "Archive: $ARCHIVE_PATH"
echo ""
echo "To install SnapSense from this package:"
echo "1. Extract the archive: tar -xzf $ARCHIVE_NAME"
echo "2. Navigate to the extracted directory: cd snapsense"
echo "3. Run the installation script: ./install.sh"
echo ""
echo "Thank you for using SnapSense!"