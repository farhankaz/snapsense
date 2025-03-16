# SnapSense

SnapSense is an intelligent screenshot renaming tool for Apple Silicon Macs that uses Anthropic's Claude AI to analyze images and generate descriptive filenames.

## Features

- Automatically monitors a configurable directory for new screenshots
- Uses Claude's vision capabilities to analyze image content
- Generates descriptive, meaningful filenames based on image content
- Runs as a background process on macOS
- Configurable scan interval and screenshot prefix
- Simple command-line interface for management

## Requirements

- macOS running on Apple Silicon
- Python 3.6 or higher
- Anthropic API key

## Installation

1. Clone or download this repository
2. Run the installation script:

```bash
chmod +x install.sh
./install.sh
```

3. Set your Anthropic API key in your environment:

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## Usage

SnapSense provides a simple command-line interface:

```bash
# Start the application in the background
snapsense start

# Check the status of the application
snapsense status

# Stop the application
snapsense stop

# Edit the configuration
snapsense config
```

## Configuration

The configuration file is located at `~/.config/snapsense/config.ini`. You can edit it directly or use the `snapsense config` command.

Default configuration:

```ini
[General]
scan_interval = 5
scan_directory = ~/Desktop
screenshot_prefix = Screenshot
max_retries = 3
retry_delay = 2
```

- `scan_interval`: How often to scan the directory (in seconds)
- `scan_directory`: The directory to monitor for screenshots
- `screenshot_prefix`: Only process files starting with this prefix
- `max_retries`: Maximum number of retries for API calls
- `retry_delay`: Delay between retries (in seconds)

## Logs

Logs are stored at `~/Library/Logs/snapsense.log`.

## How It Works

1. SnapSense monitors your configured directory for new image files
2. When a new image with the configured prefix is detected, it's sent to Claude's vision model
3. Claude analyzes the image content and suggests an appropriate filename
4. The file is renamed with the suggested name, maintaining the original file extension

## Troubleshooting

If you encounter issues:

1. Check the logs at `~/Library/Logs/snapsense.log`
2. Ensure your Anthropic API key is correctly set
3. Verify the configuration file has appropriate permissions
4. Make sure Python and required packages are installed

## License

MIT License