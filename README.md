# SnapSense

SnapSense is an intelligent screenshot renaming tool for Apple Silicon Macs that uses Anthropic's Claude AI to analyze images and generate descriptive filenames.

## The Problem SnapSense Solves

Over time, Mac users accumulate hundreds of screenshots with generic filenames like "Screenshot 2025-03-16 at 13.21.35.png" using the built-in Screenshot utility. These cryptic names make it nearly impossible to find specific screenshots using Spotlight search or Finder.

SnapSense transforms this experience by intelligently analyzing your screenshots and renaming them with meaningful, descriptive filenames that accurately reflect their content. This makes your screenshots instantly searchable and discoverable, saving you valuable time and reducing digital clutter. Whether you're a designer collecting inspiration, a developer documenting bugs, or a professional organizing meeting notes, SnapSense ensures your visual information is always at your fingertips.

## Features

- Real-time monitoring of a configurable directory using file system events
- Processes existing screenshots at startup
- Uses Claude's vision capabilities to analyze image content
- Generates descriptive, meaningful filenames based on image content
- Efficient queue-based processing system
- Runs as a background process on macOS
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
scan_directory = ~/Desktop
screenshot_prefix = Screenshot
max_retries = 3
retry_delay = 2
```

- `scan_directory`: The directory to monitor for screenshots
- `screenshot_prefix`: Only process files starting with this prefix
- `max_retries`: Maximum number of retries for API calls
- `retry_delay`: Delay between retries (in seconds)

## Logs

Logs are stored at `~/Library/Logs/snapsense.log`.

## How It Works

1. At startup, SnapSense scans your configured directory for existing screenshots and adds them to a processing queue
2. SnapSense uses file system events to detect new screenshots in real-time
3. When a new screenshot is detected, it's added to the processing queue
4. A dedicated worker thread processes images from the queue one by one
5. Each image is sent to Claude's vision model for analysis
6. Claude analyzes the image content and suggests an appropriate filename
7. The file is renamed with the suggested name, maintaining the original file extension

## Troubleshooting

If you encounter issues:

1. Check the logs at `~/Library/Logs/snapsense.log`
2. Ensure your Anthropic API key is correctly set
3. Verify the configuration file has appropriate permissions
4. Make sure Python and required packages are installed

## License

MIT License