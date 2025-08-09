# CLAUDE.md - AI Assistant Instructions

## Project Overview
Meeting Agent: Web-only application that records, transcribes, and summarizes meetings with real-time features and beautiful UI.

## Core Requirements

### 1. Web-Only Architecture (Simplified)
- **Single Entry Point**: `python app.py` starts everything
- **No CLI Complexity**: Eliminated multiple CLIs for simplicity  
- **Modern Web Interface**: Real-time updates, responsive design, mobile-friendly
- **Cloud Ready**: Deploy anywhere that runs Python web apps

### 2. Always Use Simplest & Most Efficient Approach
- Prefer straightforward solutions over complex architectures
- Optimize for performance, maintainability, and user experience
- Focus on web interface excellence over CLI features

### 3. Document All Decisions
For each request, tell me:
- What alternatives you considered
- Why you picked the current approach
- Trade-offs made

## Key Architecture Rules

**Configuration:**
- Secrets → Environment variables (OPENAI_API_KEY, PORT, DEBUG, HOST)
- Settings → `config/settings.yml` for non-sensitive settings
- No `.env` files in production

**Web Interface:**
- Enhanced dashboard with big buttons and real-time status
- Beautiful card-based design with gradients and animations
- Live transcript display during meetings
- Advanced search functionality
- One-click ChatGPT format copying

## Quick Start (Web-Only)

```bash
# 1. Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# 2. Start the application
python app.py

# 3. Open browser to http://127.0.0.1:5003
```

## Implementation Standards

1. **Security**: Never commit secrets, use environment variables
2. **Simplicity**: Single app.py entry point, no CLI complexity
3. **Cost Tracking**: All transcription operations must track costs
4. **Real-time Features**: WebSocket updates for live transcripts
5. **Mobile-Friendly**: Responsive design works on all devices

## Web Interface Features

- **🎙️ Enhanced Dashboard**: Large buttons, real-time status, live stats
- **📝 Live Transcription**: Real-time transcript display during meetings
- **🔍 Advanced Search**: Search meetings by name, participants, or content
- **📊 Daily Summaries**: Generate AI summaries for any date
- **📋 ChatGPT Integration**: One-click copy in perfect format
- **📱 Mobile Support**: Works on phones, tablets, and desktops

## Files Structure (Simplified)

```
meeting-agent/
├── app.py              # Single entry point
├── test.py             # Simple test runner
├── src/                # Core application
│   ├── main.py        # MeetingAgent class
│   ├── web/           # Web interface
│   ├── database/      # SQLite storage
│   ├── audio/         # Recording
│   ├── transcription/ # AI transcription
│   └── ai/           # AI summarization
└── config/           # Settings
```

## Deployment

**Local Development:**
```bash
python app.py
```

**Production (Environment Variables):**
```bash
export OPENAI_API_KEY="your-key"
export PORT=8080
export HOST=0.0.0.0
python app.py
```

**Docker Ready:** The web-only architecture containerizes easily

## Success Criteria
- One command starts everything: `python app.py`
- Beautiful, intuitive web interface
- Real-time features work smoothly
- Mobile-friendly responsive design  
- Primary workflows are seamless: record → view → copy to ChatGPT