#!/usr/bin/env python3
"""
Interactive setup script to configure API keys
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Interactive setup for API keys"""
    print("🔧 Meeting Agent API Setup")
    print("=" * 30)
    print()
    
    # Get OpenAI API Key
    print("1. OpenAI API Key Setup:")
    current_openai = os.environ.get('OPENAI_API_KEY', '')
    if current_openai:
        print(f"   Current: {current_openai[:10]}...")
        if input("   Use existing key? (y/n): ").lower() != 'y':
            current_openai = ''
    
    if not current_openai:
        openai_key = input("   Enter OpenAI API key (sk-...): ").strip()
        if openai_key.startswith('sk-'):
            os.environ['OPENAI_API_KEY'] = openai_key
            print("   ✅ OpenAI key set")
        else:
            print("   ❌ Invalid OpenAI key format")
            return False
    
    # Get Email Settings  
    print("\n2. Email Setup:")
    current_email = os.environ.get('EMAIL_ADDRESS', '')
    if current_email:
        print(f"   Current email: {current_email}")
        if input("   Use existing email? (y/n): ").lower() != 'y':
            current_email = ''
    
    if not current_email:
        email_address = input("   Enter Gmail address: ").strip()
        if '@' in email_address:
            os.environ['EMAIL_ADDRESS'] = email_address
            print("   ✅ Email address set")
        else:
            print("   ❌ Invalid email format")
            return False
    
    current_password = os.environ.get('EMAIL_PASSWORD', '')
    if current_password:
        print("   Email password already set")
        if input("   Update password? (y/n): ").lower() == 'y':
            current_password = ''
    
    if not current_password:
        print("   Note: Use Gmail App Password (not regular password)")
        print("   Generate at: https://myaccount.google.com/apppasswords")
        email_password = input("   Enter Gmail app password: ").strip()
        if len(email_password) >= 8:
            os.environ['EMAIL_PASSWORD'] = email_password
            print("   ✅ Email password set")
        else:
            print("   ❌ Password too short")
            return False
    
    # Create .env file for persistence
    env_file = Path('.env')
    print(f"\n3. Creating .env file at {env_file.absolute()}")
    
    with open(env_file, 'w') as f:
        f.write(f"# Meeting Agent Environment Variables\n")
        f.write(f"OPENAI_API_KEY={os.environ.get('OPENAI_API_KEY', '')}\n")
        f.write(f"EMAIL_ADDRESS={os.environ.get('EMAIL_ADDRESS', '')}\n")
        f.write(f"EMAIL_PASSWORD={os.environ.get('EMAIL_PASSWORD', '')}\n")
    
    print(f"   ✅ Environment file created")
    print(f"\n🎉 Setup complete!")
    print(f"\nNext steps:")
    print(f"1. Source the environment: source .env")
    print(f"2. Or restart your terminal")
    print(f"3. Run: python test_real_apis.py")
    
    return True

def create_direct_config():
    """Create config file with direct key insertion"""
    print("\n4. Alternative: Direct Config File")
    print("   This will create config/config.yaml with your keys directly")
    
    if input("   Create direct config file? (y/n): ").lower() == 'y':
        
        openai_key = os.environ.get('OPENAI_API_KEY') or input("   OpenAI API Key: ")
        email_addr = os.environ.get('EMAIL_ADDRESS') or input("   Email Address: ")
        email_pass = os.environ.get('EMAIL_PASSWORD') or input("   Email Password: ")
        
        config_dir = Path('config')
        config_dir.mkdir(exist_ok=True)
        
        config_content = f"""# Meeting Agent Configuration
# Direct API key configuration (not recommended for production)

openai:
  api_key: "{openai_key}"
  transcription_model: "whisper-1"
  summarization_model: "gpt-4"

email:
  address: "{email_addr}"
  password: "{email_pass}"
  smtp_server: "smtp.gmail.com"
  smtp_port: 587

database:
  path: "data/meetings.db"

audio:
  sample_rate: 44100
  channels: 2
  chunk_size: 1024

web:
  secret_key: "meeting-agent-secret-key"
  host: "localhost"
  port: 5000
"""
        
        config_file = config_dir / 'config.yaml'
        with open(config_file, 'w') as f:
            f.write(config_content)
            
        print(f"   ✅ Direct config created at {config_file}")
        print(f"   ⚠️  Warning: API keys are stored in plain text")
        
        return True
    
    return False

if __name__ == "__main__":
    if setup_environment():
        create_direct_config()
    else:
        print("\n❌ Setup failed")
        sys.exit(1)