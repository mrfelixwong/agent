#!/usr/bin/env python3
"""
Log monitoring script for Meeting Agent
Shows real-time logs from all components
"""

import sys
import time
import subprocess
from pathlib import Path

def monitor_logs():
    """Monitor logs in real-time"""
    logs_dir = Path(__file__).parent / "logs"
    
    print("🔍 Meeting Agent Log Monitor")
    print("=" * 40)
    print(f"📁 Logs directory: {logs_dir}")
    
    if not logs_dir.exists():
        print("⚠️ Logs directory doesn't exist yet. Start the application first.")
        return
    
    log_files = [
        logs_dir / "meeting_agent.log",
        logs_dir / "web_interface.log"
    ]
    
    existing_logs = [log for log in log_files if log.exists()]
    
    if not existing_logs:
        print("⚠️ No log files found yet. Start the application first.")
        print("\nAvailable commands:")
        print("  python start_web.py    - Start web interface")
        return
    
    print(f"📄 Monitoring {len(existing_logs)} log files:")
    for log in existing_logs:
        print(f"  • {log.name}")
    
    print("\n🔍 Real-time logs (Press Ctrl+C to stop):")
    print("-" * 60)
    
    try:
        # Use tail -f to follow multiple log files
        cmd = ['tail', '-f'] + [str(log) for log in existing_logs]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        while True:
            output = process.stdout.readline()
            if output:
                # Color code different log levels
                if 'ERROR' in output:
                    print(f"\033[91m{output.strip()}\033[0m")  # Red
                elif 'WARNING' in output:
                    print(f"\033[93m{output.strip()}\033[0m")  # Yellow
                elif 'INFO' in output:
                    print(f"\033[92m{output.strip()}\033[0m")  # Green
                elif 'DEBUG' in output:
                    print(f"\033[94m{output.strip()}\033[0m")  # Blue
                else:
                    print(output.strip())
            elif process.poll() is not None:
                break
                
    except KeyboardInterrupt:
        print("\n👋 Log monitoring stopped")
        if 'process' in locals():
            process.terminate()
    except FileNotFoundError:
        print("❌ 'tail' command not found. Falling back to simple monitoring...")
        
        # Fallback: simple file monitoring
        try:
            positions = {log: log.stat().st_size if log.exists() else 0 for log in existing_logs}
            
            while True:
                for log_file in existing_logs:
                    if log_file.exists():
                        current_size = log_file.stat().st_size
                        if current_size > positions[log_file]:
                            with open(log_file, 'r') as f:
                                f.seek(positions[log_file])
                                new_content = f.read()
                                if new_content.strip():
                                    print(f"[{log_file.name}] {new_content.strip()}")
                                positions[log_file] = current_size
                
                time.sleep(0.5)  # Check every 500ms
                
        except KeyboardInterrupt:
            print("\n👋 Log monitoring stopped")

def show_recent_logs():
    """Show recent log entries"""
    logs_dir = Path(__file__).parent / "logs"
    
    if not logs_dir.exists():
        print("⚠️ Logs directory doesn't exist yet.")
        return
    
    log_files = [
        logs_dir / "meeting_agent.log",
        logs_dir / "web_interface.log"
    ]
    
    print("📄 Recent Log Entries (last 20 lines per file):")
    print("=" * 50)
    
    for log_file in log_files:
        if log_file.exists():
            print(f"\n🔍 {log_file.name}:")
            print("-" * 30)
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    for line in recent_lines:
                        print(line.rstrip())
            except Exception as e:
                print(f"Error reading {log_file}: {e}")
        else:
            print(f"\n⚠️ {log_file.name}: File doesn't exist yet")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--recent':
        show_recent_logs()
    else:
        monitor_logs()