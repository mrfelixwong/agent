# Meeting Agent Setup Guide

## Quick Start (Demo Mode)

The system is ready to run with mock components for testing:

```bash
# Run the demo
python demo.py

# Run integration tests
python test_integration.py

# Interactive CLI
python cli.py
```

## Production Setup

### 1. Install Dependencies

```bash
# Core dependencies
pip install pyaudio openai pyyaml flask flask-socketio

# macOS specific (if needed)
brew install portaudio
```

### 2. Configure API Keys

Edit `config/config.yaml`:

```yaml
openai:
  api_key: "your-openai-api-key-here"
  transcription_model: "whisper-1"
  summarization_model: "gpt-4"

email:
  address: "your-email@gmail.com"
  password: "your-app-password"  # Generate app password in Gmail
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
```

### 3. Gmail Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an app password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Meeting Agent"
   - Use this password (not your Gmail password) in config

### 4. Run Production System

```bash
# Start with real components
python -c "from src.main import MeetingAgent; agent = MeetingAgent(use_mock_components=False)"

# Or modify cli.py to set use_mock_components=False
```

## Features

### ✅ Implemented

- **Audio Recording**: System audio capture with PyAudio
- **Real-time Transcription**: OpenAI Whisper integration  
- **AI Summarization**: GPT-4 powered meeting summaries
- **Email Notifications**: Immediate and daily summary emails
- **Web Interface**: Simple HTML dashboard and REST API
- **Database Storage**: SQLite for meeting persistence
- **Search & History**: Find meetings by content
- **CLI Interface**: Interactive command-line control

### 📋 Architecture

```
Meeting Agent
├── Audio Recording (PyAudio)
├── Transcription (OpenAI Whisper)
├── AI Summary (OpenAI GPT)
├── Email (Gmail SMTP)
├── Database (SQLite)
├── Web UI (Flask)
└── Main Orchestrator
```

### 🎛️ Controls

- **Manual Start/Stop**: Full control over recording
- **Real-time Display**: Live transcript during meetings
- **Automatic Processing**: Summary and email after meeting
- **Meeting Management**: History, search, and details

## Usage

### Via CLI
```bash
python cli.py
# Select options 1-7 for different functions
```

### Via Web Interface
```bash
python cli.py  # Select option 7
# Navigate to http://localhost:5000
```

### Via API
```python
from src.main import MeetingAgent

agent = MeetingAgent()
meeting = agent.start_meeting("Team Standup", ["Alice", "Bob"])
# ... recording happens ...
completed = agent.stop_meeting()
```

## File Structure

```
agent/
├── src/
│   ├── audio/          # Audio recording components
│   ├── transcription/  # Real-time transcription
│   ├── ai/            # AI summarization
│   ├── notifications/ # Email system
│   ├── database/      # Data persistence
│   ├── web/          # Flask web interface
│   ├── utils/        # Configuration and logging
│   └── main.py       # Main orchestrator
├── config/
│   └── config.yaml   # Configuration file
├── data/            # Database and recordings (auto-created)
├── tests/           # Unit tests
├── cli.py          # Command-line interface
├── demo.py         # Demonstration script
└── test_integration.py  # Integration tests
```

## Testing

```bash
# Run all tests
python test_integration.py

# Test individual components
python -m tests.test_audio
python -m tests.test_transcription
# etc.

# Demo workflow
python demo.py
```

## Troubleshooting

### PyAudio Installation Issues

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

### API Key Issues

- Ensure OpenAI API key has sufficient credits
- Gmail app password must be generated (not regular password)
- Check internet connectivity for API calls

### Permission Issues

- Grant microphone access on macOS/Windows
- Run as administrator if needed for audio access

## Daily Email Scheduling

To enable 10pm daily emails, add to crontab:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path)
0 22 * * * cd /path/to/agent && python -c "from src.main import MeetingAgent; MeetingAgent().send_daily_summary_email()"
```

## Security Notes

- API keys are stored in plain text - consider environment variables for production
- Meeting audio and transcripts contain sensitive data - ensure proper access controls
- Email credentials should use app passwords, not main account passwords