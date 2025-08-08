# Environment Variables Setup

This project uses a **hybrid configuration approach**:
- **Secrets** (API keys, passwords) → Environment variables in `~/.zshrc`  
- **Settings** (ports, models, paths) → Configuration file `config/settings.yml`

**⚠️ Important: DO NOT create a `.env` file - use your shell profile for secrets only!**

## Required Secrets

Add these **SECRET** variables to your `~/.zshrc` file:

```bash
# Meeting Agent - Required Secrets (add to ~/.zshrc)
export OPENAI_API_KEY="your_actual_openai_api_key_here"
export EMAIL_ADDRESS="your_email@example.com" 
export EMAIL_PASSWORD="your_app_specific_password"
```

## Optional Secrets

Add these to `~/.zshrc` if you need them:

```bash
# Meeting Agent - Optional Secrets (add to ~/.zshrc)
export SECRET_KEY="your_web_secret_key_for_sessions"
```

## Non-Secret Configuration

**Non-sensitive settings** are in `config/settings.yml` and can be modified directly:
- Web server host/port (5002)
- OpenAI model names (whisper-1, gpt-4)
- Audio settings (sample rate, channels)
- Database paths
- Logging configuration

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