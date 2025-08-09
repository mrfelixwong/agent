#!/usr/bin/env python3
"""
Simple script to clear the meeting database
Usage: python clear_db.py
"""

import sqlite3
import os
from pathlib import Path

def clear_database():
    """Clear all data from the meetings database"""
    
    # Database path
    db_path = Path("data/meetings.db")
    
    if not db_path.exists():
        print("❌ Database file not found at:", db_path)
        return
    
    print("🗑️  Clearing meeting database...")
    
    try:
        # Connect and clear
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Count current meetings
            cursor.execute("SELECT COUNT(*) FROM meetings")
            meeting_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM daily_summaries") 
            summary_count = cursor.fetchone()[0]
            
            print(f"📊 Found {meeting_count} meetings and {summary_count} daily summaries")
            
            if meeting_count == 0 and summary_count == 0:
                print("✅ Database is already empty!")
                return
            
            # Clear all data
            cursor.execute("DELETE FROM meetings")
            cursor.execute("DELETE FROM daily_summaries")
            
            conn.commit()
            
        print(f"✅ Deleted {meeting_count} meetings and {summary_count} daily summaries")
        print("🧹 Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    clear_database()