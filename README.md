# Meeting Agent

An intelligent meeting assistant that automatically records, transcribes, and summarizes your meetings with daily email reports.

## Features

- **Automatic Meeting Detection**: Integrates with calendar systems to detect upcoming meetings
- **Audio Recording**: Records meeting audio with participant consent
- **Real-time Transcription**: Converts speech to text using advanced AI models
- **AI-Powered Summaries**: Generates concise meeting summaries with key points
- **Action Item Extraction**: Identifies and tracks action items and decisions
- **Daily Email Reports**: Sends comprehensive daily summaries via email
- **Privacy-First**: Local processing with optional cloud AI integration

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Calendar      │    │  Audio Capture  │    │  Transcription  │
│   Integration   │───▶│     System      │───▶│    Service      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scheduling    │    │   AI Summary    │    │    Database     │
│    Service      │    │   Generation    │◀───│    Storage      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ Email Service   │    │  Web Dashboard  │
│ (Daily Reports) │    │   (Optional)    │
└─────────────────┘    └─────────────────┘
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**:
   ```bash
   cp config/settings.example.yml config/settings.yml
   # Edit with your API keys and preferences
   ```

3. **Run the Agent**:
   ```bash
   python src/main.py
   ```

4. **Web Interface** (Optional):
   ```bash
   python src/web_app.py
   # Visit http://localhost:5000
   ```

## Configuration

### Required Settings
- **OpenAI API Key**: For transcription and summarization
- **Email SMTP**: For sending daily reports
- **Calendar Integration**: Google Calendar, Outlook, etc.

### Optional Integrations
- **Zoom SDK**: For automatic Zoom meeting recording
- **Microsoft Teams**: Teams meeting integration
- **Slack**: Slack huddle and meeting support

## Privacy & Compliance

- All audio processing can be done locally
- Transcripts encrypted at rest
- GDPR and privacy regulation compliant
- Participant consent management
- Data retention policies configurable

## Usage Examples

### Manual Meeting Recording
```python
from src.meeting_recorder import MeetingRecorder

recorder = MeetingRecorder()
meeting_id = recorder.start_recording("Team Standup")
# ... meeting happens ...
summary = recorder.stop_and_summarize(meeting_id)
```

### Calendar Integration
```python
from src.calendar_integration import CalendarWatcher

watcher = CalendarWatcher()
watcher.start_monitoring()  # Automatically handles upcoming meetings
```

## Email Report Examples

### Individual Meeting Summary
```
Subject: Meeting Summary: Product Planning Session

Meeting: Product Planning Session
Date: March 15, 2024, 2:00 PM - 3:30 PM
Participants: Alice Johnson, Bob Smith, Carol Davis

## Key Discussion Points
• Q2 feature roadmap priorities
• Resource allocation for new initiatives
• Customer feedback integration process

## Decisions Made
• Move forward with mobile app redesign
• Allocate 2 additional developers to Project Phoenix
• Implement weekly customer feedback reviews

## Action Items
• Alice: Create detailed mobile app wireframes (Due: March 22)
• Bob: Hire 2 senior developers (Due: April 1)  
• Carol: Set up customer feedback pipeline (Due: March 20)

## Next Steps
• Follow-up meeting scheduled for March 22
• Review progress on action items
```

### Daily Summary Report
```
Subject: Daily Meeting Summary - March 15, 2024

You had 4 meetings today totaling 5 hours and 30 minutes.

## Meeting Overview
1. **Team Standup** (30 min) - Routine check-in, no action items
2. **Product Planning** (90 min) - Major decisions on Q2 roadmap
3. **Client Call - Acme Corp** (60 min) - Requirements gathering
4. **Budget Review** (90 min) - Q1 spending analysis

## Top Action Items Across All Meetings
1. Create mobile app wireframes (Due: March 22)
2. Prepare Q1 budget variance report (Due: March 18)
3. Schedule Acme Corp follow-up (Due: March 16)
4. Review developer hiring plan (Due: April 1)

## Key Themes
• **Resource Planning**: Multiple discussions about team expansion
• **Customer Focus**: Emphasis on user feedback and client needs  
• **Q2 Preparation**: Strategic planning for next quarter initiatives

## Meeting Efficiency Score: 8.2/10
Based on: Action item clarity, decision making, time management
```

## Development

### Project Structure
```
agent/
├── src/
│   ├── main.py                 # Main application entry
│   ├── meeting_recorder.py     # Audio recording logic
│   ├── transcription.py        # Speech-to-text service
│   ├── summarization.py        # AI-powered summarization
│   ├── email_service.py        # Email notification system
│   ├── calendar_integration.py # Calendar API integrations
│   ├── database.py             # Data storage layer
│   └── web_app.py              # Optional web interface
├── config/
│   ├── settings.yml            # Main configuration
│   └── email_templates/        # Email template files
├── tests/                      # Test suite
├── docs/                       # Additional documentation
└── scripts/                    # Utility scripts
```

### Technology Stack
- **Python 3.9+**: Core application
- **OpenAI Whisper**: Speech transcription
- **OpenAI GPT**: Text summarization
- **SQLite/PostgreSQL**: Data storage
- **APScheduler**: Task scheduling
- **Flask**: Web interface (optional)
- **SMTP**: Email delivery

## Deployment

### Local Development
```bash
git clone <repository>
cd agent
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### Production Deployment
- Docker container available
- Supports deployment to AWS, GCP, Azure
- Can run as system service/daemon
- Kubernetes manifests included

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issue
- Check documentation in `/docs`
- Email: support@meetingagent.com