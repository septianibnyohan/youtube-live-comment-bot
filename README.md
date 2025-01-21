# YouTube Live Comment Bot

A powerful and customizable YouTube automation tool built with Python and PyQt6 for managing YouTube live chat interactions.

## Features

### Core Features
- **Flexible Start Options**
  - Immediate execution
  - Scheduled runs with customizable intervals
  - Day-of-week scheduling

### Browser Configuration
- **Browser Control**
  - Multiple browser support (Chrome, Firefox, Edge)
  - Custom user agent management
  - Premium fingerprint support

### Connection Management
- **Connection Types**
  - Proxy support
  - VPN integration
  - Direct connection

### Device Emulation
- Desktop mode
- Mobile mode
- Random device rotation

### Traffic Sources
- Keyword-based navigation
- YouTube Music integration
- Channel playlist browsing
- External referrers

### Automation Features
- **Human Emulation**
  - Customizable watching duration
  - View count management
  - Smart video navigation
  - Natural timing variations

### Security Features
- Browser history management
- Double IP prevention
- Whoer.net score verification
- Timezone consistency checks
- Residential IP verification

### Interaction Features
- Live chat commenting
- Video likes
- Channel subscriptions
- Comment speed control
- Maximum comments per user

## Requirements

- Python 3.8+
- Chrome/Firefox/Edge browser
- Active internet connection
- (Optional) Proxy or VPN service

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-live-bot.git
cd youtube-live-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Basic Usage

1. Start the application:
```bash
python src/main.py
```

2. Configure your settings in the GUI:
   - Set browser preferences
   - Configure proxy settings (if using)
   - Set up automation rules
   - Add your comment pool

3. Click "Start" to begin automation

### Advanced Configuration

#### Proxy Setup

Create a `proxies.txt` file in the `resources/data` directory:
```text
protocol://username:password@host:port
```

#### Comment Pool

Create a `comments.txt` file in the `resources/data` directory:
```text
One comment per line
Multiple lines supported
{variables} can be used
```

#### Schedule Configuration

Schedule format in `config/default.json`:
```json
{
  "schedule": {
    "type": "interval",
    "value": 30,
    "unit": "minutes"
  }
}
```

## Configuration Options

### Browser Settings
```json
{
  "browser": {
    "type": "chrome",
    "headless": false,
    "user_agent": "custom_agent_string",
    "fingerprint": true
  }
}
```

### Proxy Settings
```json
{
  "proxy": {
    "enabled": true,
    "type": "http",
    "rotation_interval": 300,
    "min_score": 70
  }
}
```

### Automation Settings
```json
{
  "automation": {
    "watch_duration": {
      "min": 30,
      "max": 300
    },
    "comment_interval": 5,
    "max_comments_per_user": 5
  }
}
```

## Safety Features

### Proxy Verification
- Whoer.net score must be above 70%
- Residential IP verification
- Timezone consistency checks

### Browser Security
- Automatic history cleaning
- Cookie management
- Fingerprint rotation

### Rate Limiting
- Comment speed controls
- View duration randomization
- Action interval management

## Development

### Project Structure
```
youtube_bot/
├── src/
│   ├── gui/       # GUI components
│   ├── core/      # Core functionality
│   ├── browser/   # Browser automation
│   ├── proxy/     # Proxy management
│   └── utils/     # Utilities
├── tests/         # Test files
├── docs/          # Documentation
└── resources/     # Application resources
```

### Running Tests
```bash
pytest tests/
```

### Building Documentation
```bash
cd docs
make html
```

## Troubleshooting

### Common Issues

1. Browser Launch Fails
```
Error: Could not launch browser
Solution: Ensure browser is installed and webdriver is compatible
```

2. Proxy Connection Failed
```
Error: Could not connect to proxy
Solution: Verify proxy settings and credentials
```

3. YouTube Detection
```
Error: Activity flagged as automated
Solution: Adjust human emulation settings and timing
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Selenium WebDriver team
- PyQt6 developers
- Python community

## Disclaimer

This tool is for educational purposes only. Users are responsible for complying with YouTube's terms of service and applicable laws. The developers assume no liability for misuse of this software.