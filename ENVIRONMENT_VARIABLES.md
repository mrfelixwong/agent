# Environment Variables Setup

This project uses environment variables stored in your shell profile (`~/.zshrc`) for security.

**⚠️ Important: DO NOT create a `.env` file - use your shell profile instead!**

## Required Setup

Add these lines to your `~/.zshrc` file:

```bash
# Meeting Agent - Required Variables
export OPENAI_API_KEY="your_actual_openai_api_key_here"
export EMAIL_ADDRESS="your_email@example.com"
export EMAIL_PASSWORD="your_app_specific_password"
```

## Optional Variables

Add these to `~/.zshrc` if you want to customize defaults:

```bash
# Meeting Agent - Optional Variables  
export WEB_HOST="localhost"
export WEB_PORT="5002" 
export SECRET_KEY="your_web_secret_key"
export FLASK_DEBUG="false"
export DATABASE_URL="sqlite:///data/database.db"
export DAILY_SUMMARY_TIME="22:00"
export AUDIO_SAMPLE_RATE="44100"
export AUDIO_CHANNELS="2"
export LOG_LEVEL="INFO"
```

## After Adding Variables

Reload your shell:
```bash
source ~/.zshrc
```

## Why ~/.zshrc Instead of .env?

- **More secure**: Environment variables are available system-wide
- **Persistent**: Variables survive terminal sessions
- **No accidental commits**: No risk of committing secrets to git
- **Standard practice**: Follows Unix/Linux conventions