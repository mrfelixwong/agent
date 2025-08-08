# Logging Guide

## Current Logging Status: ✅ EXCELLENT

The Meeting Agent now has comprehensive logging for debugging and monitoring.

## 📊 Logging Coverage Summary

### ✅ What's Logged (150+ log statements)

**Error Handling** (50+ error logs)
- All exceptions caught and logged with context
- API failures with retry information
- Component initialization failures
- Graceful degradation scenarios

**Key Operations** (70+ info logs)
- Meeting lifecycle (start/stop/status)
- Component initialization and cleanup
- Database operations with results
- Cost tracking with detailed breakdown
- API calls with timing and response info

**Debug Information** (20+ debug logs)
- Audio chunk processing details
- Configuration loading steps
- API request/response timing
- Performance metrics for key operations
- Business logic decision points

## 🎛️ Log Levels

**INFO** (Default Production)
```yaml
# config/settings.yml
logging:
  level: INFO  # Shows normal operations and important events
```

**DEBUG** (Development/Troubleshooting)
```yaml
# config/settings.yml  
logging:
  level: DEBUG  # Shows detailed execution flow and performance
```

**To enable debug logging temporarily:**
```bash
# Edit config/settings.yml level to DEBUG, then restart
python start_web.py
```

## 🔍 Key Debug Features

**Performance Monitoring**
```python
@log_performance  # Decorator logs execution time
def summarize_meeting(...):  # AI summary timing
def transcribe_audio(...):   # API call latency
```

**Audio Processing Details**
- Chunk count and sizes
- WAV file generation stats
- API request timing
- Cost calculations per chunk

**Configuration Loading**
- YAML file loading status
- Environment variable detection
- Hybrid config merge process

## 📂 Log Output

**Console Output** (Always enabled)
```
2025-08-08 10:47:43,022 - src.main - INFO - Meeting started: Weekly Standup
2025-08-08 10:47:45,341 - src.transcription.transcriber - INFO - Transcribed 3.2s of audio (cost: $0.0003, API time: 1.45s)
```

**Log Files** (When configured)
```
logs/meeting_agent.log       # Main log file
logs/meeting_agent.log.1     # Rotated backup (10MB rotation, 5 backups)
```

## 🐛 Debugging Common Issues

**Meeting Won't Start**
```bash
# Look for these log patterns:
grep "Failed to start meeting" logs/meeting_agent.log
grep "Audio initialization" logs/meeting_agent.log
```

**Transcription Issues**
```bash
# Enable DEBUG logging and check:
grep "Whisper API" logs/meeting_agent.log
grep "audio chunks" logs/meeting_agent.log
grep "Transcription error" logs/meeting_agent.log
```

**Cost Tracking Problems**
```bash
# Check cost calculations:
grep "cost:" logs/meeting_agent.log
grep "Total transcription cost" logs/meeting_agent.log
```

**API Failures**
```bash
# OpenAI API issues:
grep "OpenAI" logs/meeting_agent.log
grep "API.*failed" logs/meeting_agent.log
```

**Configuration Issues**
```bash
# Config loading problems:
grep "Loading configuration" logs/meeting_agent.log
grep "Missing required secrets" logs/meeting_agent.log
```

## ⚡ Performance Analysis

**Enable DEBUG logging to see:**
- Function execution times
- API response latencies
- Audio processing bottlenecks
- Database query performance
- Memory usage patterns

**Sample Debug Output:**
```
DEBUG - summarize_meeting completed in 2.341s
DEBUG - Processing 15 audio chunks  
DEBUG - Sending 3.2s of audio to Whisper API
DEBUG - Transcript length: 247 characters
```

## 🛠️ Logging Best Practices

**For Developers:**
1. Use `logger.debug()` for detailed flow information
2. Use `logger.info()` for important business events
3. Use `logger.warning()` for recoverable issues
4. Use `logger.error()` for failures that need attention

**For Production:**
1. Keep level at INFO to balance detail vs. performance
2. Monitor log file sizes (auto-rotation at 10MB)
3. Check logs regularly for WARNING/ERROR patterns
4. Use DEBUG temporarily when investigating issues

**Log Format:**
```
TIMESTAMP - MODULE - LEVEL - MESSAGE
2025-08-08 10:47:43,022 - src.main - INFO - Meeting Agent initialized successfully
```

The logging system is now production-ready with excellent debugging capabilities! 🎯