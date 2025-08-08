# CLAUDE.md - Project Instructions

## Project Overview
This is a Meeting Agent that records, transcribes, and summarizes meetings with cost tracking and a web interface.

## Key Architecture Decisions

### Configuration System (Hybrid Approach)
- **Secrets** (API keys, passwords) → Environment variables in `~/.zshrc`
- **Settings** (ports, models, paths) → Config file `config/settings.yml` 
- **Never** create `.env` files - always use shell profile for secrets

### File Structure
- `src/` - Main application code
- `production_cli.py` - Primary entry point
- `start_web.py` - Web interface launcher
- `tests/` - Unit tests (keep these)
- `test_*.py` - Integration tests (keep these)

### Important Rules

1. **Security First**
   - Never commit API keys or secrets
   - Always use environment variables for sensitive data
   - Keep non-sensitive settings in YAML config files

2. **Code Quality**
   - Remove unnecessary debug/demo files
   - Keep the codebase clean and focused
   - Maintain proper separation of concerns

3. **Environment Variables**
   - Only for secrets: `OPENAI_API_KEY`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD`
   - Users should add these to `~/.zshrc`, not `.env` files
   - Validate secrets only for real components, skip for mock components

4. **Cost Tracking**
   - Track transcription costs ($0.006/minute default)
   - Store in database and display in UI
   - Make cost per minute configurable in settings.yml

5. **Testing**
   - Use mock components for testing (`use_mock_components=True`)
   - Keep integration tests for real API validation
   - Always test web interface functionality

## Development Guidelines

- Use the hybrid configuration system (secrets in env, settings in YAML)
- Maintain cost tracking for all transcription operations
- Keep the web interface simple and functional
- Follow the existing code patterns and structure
- Always validate configuration but skip validation for mocks

## Files to Never Recreate
- setup_env.py (removed - use ~/.zshrc instead)
- .env files (use environment variables)
- Debug/demo files (keep codebase clean)
- Empty placeholder directories

## When Making Changes
1. Test with `python test_web.py`
2. Ensure mock components work without secrets
3. Maintain the hybrid config approach
4. Keep cost tracking functionality intact
5. Update documentation if architecture changes