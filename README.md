# Meeting Agent

An intelligent meeting assistant that records, transcribes, and summarizes meetings with real-time transcript display, cost tracking, and ChatGPT-ready export functionality.

## 🚀 Features

- **Real-time Recording**: Start/stop meetings with live transcript display
- **AI-Powered Transcription**: Using OpenAI Whisper with cost tracking
- **Smart Summaries**: Automatic meeting summaries with key points and action items
- **ChatGPT Integration**: One-click copy for AI-powered meeting analysis
- **Web Interface**: Clean dashboard with meeting history and detailed views
- **Cost Tracking**: Monitor transcription costs ($0.006/minute)
- **Export Options**: Markdown, JSON, and clipboard-ready formats

## 🎯 Quick Start

### 1. Setup Environment Variables

Add these secrets to your `~/.zshrc` (never use `.env` files):

```bash
# Required API keys
export OPENAI_API_KEY="your_openai_api_key_here"
export EMAIL_ADDRESS="your_email@example.com"
export EMAIL_PASSWORD="your_app_specific_password"

# Optional
export SECRET_KEY="your_web_session_key"
```

Then reload: `source ~/.zshrc`

### 2. Install Dependencies

```bash
git clone <your-repo-url>
cd agent
pip install -r requirements.txt
pip install flask-socketio  # For real-time features
```

### 3. Run the Application

```bash
# Start web interface (recommended)
python start_web.py

# Or run CLI version
python production_cli.py
```

Visit **http://localhost:5002** for the web dashboard.

## 🖥️ Web Interface

### Dashboard
- **Start/Stop Recording**: Simple meeting controls
- **Live Transcript**: Real-time text display during meetings
- **Connection Status**: WebSocket connectivity indicator
- **Cost Tracking**: Live transcription cost monitoring

### Meeting Management
- **Meeting History**: View all past meetings with status and costs
- **Detailed Views**: Rich meeting summaries with structured data
- **Copy for ChatGPT**: One-click export in AI-friendly format
- **Export Options**: Download as Markdown or JSON

### Key Workflows

1. **Record Meeting**: Click "Start Meeting" → enter name → see live transcript
2. **Stop & Review**: Click "Stop Recording" → automatic summary generation  
3. **Analyze with AI**: Open meeting details → "Copy for ChatGPT" → paste to AI
4. **Export Data**: Use Markdown export for documentation or sharing

## 📋 Meeting Summary Format

The ChatGPT export creates perfectly formatted summaries:

```
MEETING SUMMARY - Weekly Standup (2025-01-15)

CONTEXT:
Meeting with 3 participants, 45 minutes duration

KEY DECISIONS:
- Move project deadline to January 25th
- Allocate $5,000 for external design contractor

ACTION ITEMS:
- Alice: Complete design mockups by January 20th
- Bob: Review security audit by January 18th

DISCUSSION POINTS:
- Timeline concerns due to design complexity
- Budget discussion for additional resources

Please help me analyze this meeting and suggest:
1. Risk mitigation for the delayed timeline
2. Follow-up questions for the client meeting
3. Resource allocation recommendations
```

## ⚙️ Configuration

### Settings File: `config/settings.yml`

Non-sensitive settings (safe to commit):

```yaml
# Web Interface
web:
  host: localhost
  port: 5002

# Audio Recording  
audio:
  sample_rate: 44100
  channels: 1  # Mono for better compatibility

# OpenAI Models
openai:
  transcription_model: "whisper-1" 
  summarization_model: "gpt-4"

# Cost Tracking
cost:
  whisper_per_minute: 0.006  # USD per minute
```

### Environment Variables

Secrets (add to `~/.zshrc`):

- `OPENAI_API_KEY`: Required for transcription and summarization
- `EMAIL_ADDRESS`: For sending meeting summaries
- `EMAIL_PASSWORD`: App-specific password for email
- `SECRET_KEY`: Web session security (optional)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Web Dashboard  │    │  Meeting Agent  │    │  OpenAI APIs    │
│  (port 5002)    │◀──▶│   (main.py)     │◀──▶│  (Whisper/GPT)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         ▼                       ▼                       
┌─────────────────┐    ┌─────────────────┐              
│  Real-time UI   │    │  SQLite DB      │              
│  (WebSocket)    │    │  (meetings.db)  │              
└─────────────────┘    └─────────────────┘              
```

### Key Components

- **Meeting Agent** (`src/main.py`): Core orchestrator
- **Web Interface** (`src/web/app.py`): Flask app with SocketIO
- **Transcriber** (`src/transcription/transcriber.py`): Real-time speech-to-text
- **Database** (`src/database/database.py`): Meeting storage with cost tracking
- **Templates** (`src/web/templates/`): Structured meeting views

## 📊 Project Structure

```
agent/
├── src/                     # Main application code
│   ├── main.py             # Meeting Agent orchestrator
│   ├── web/                # Web interface
│   │   ├── app.py         # Flask app with templates
│   │   └── templates/     # HTML templates
│   ├── transcription/     # Speech-to-text
│   ├── database/          # Data storage
│   └── utils/             # Configuration, logging
├── config/
│   └── settings.yml       # Non-sensitive configuration
├── start_web.py          # Web interface launcher
├── production_cli.py     # CLI interface
└── CLAUDE.md            # AI assistant instructions
```

## 🧪 Testing

```bash
# Test web interface (uses mock components)
python test_web.py

# Test core functionality
python -c "
from src.main import MeetingAgent
agent = MeetingAgent(use_mock_components=True)
meeting = agent.start_meeting('Test Meeting')
print('✅ Meeting started:', meeting['name'])
agent.cleanup()
"
```

## 🎨 Features Showcase

### Real-time Transcript Display
- Live text updates during meetings
- Auto-scrolling with word count tracking
- Connection status indicators
- Toggle visibility controls

### Smart Meeting Management  
- Status indicators (Recording, Completed, etc.)
- Cost tracking with running totals
- Participant management
- Duration monitoring

### ChatGPT-Ready Export
- Pre-formatted for AI analysis
- Structured sections (Decisions, Action Items, etc.)
- Context-rich formatting
- One-click clipboard copy

### Professional UI
- Clean, responsive design
- Consistent navigation
- Professional styling
- Mobile-friendly layout

## 🔧 Development

### Mock vs Real Components
- **Development**: Use `use_mock_components=True` for testing without API keys
- **Production**: Use real components with environment variables set

### Adding Features
1. Follow hybrid approach: simple for basic features, structured for complex data
2. Document alternatives considered and reasoning
3. Maintain cost tracking for any transcription features
4. Test with both mock and real components

## 💡 Future Ideas

- **Desktop App**: System tray application for easier startup
- **Mobile App**: React Native or Flutter companion app
- **Calendar Integration**: Automatic meeting detection
- **Team Features**: Multi-user support and permissions
- **Advanced Analytics**: Meeting efficiency scoring

## 📝 License

MIT License - see LICENSE file for details.

## 🛠️ Troubleshooting

### Common Issues

1. **Port 5002 in use**: Change port in `config/settings.yml`
2. **Missing API keys**: Check `~/.zshrc` and run `source ~/.zshrc`
3. **Template errors**: Ensure `src/web/templates/` directory exists
4. **WebSocket issues**: Check if Flask-SocketIO is installed

### Getting Help

- Check logs in `logs/meeting_agent.log` (if enabled)
- Use debug mode: Set `logging.level: DEBUG` in `config/settings.yml`
- Test with mock components first: `use_mock_components=True`