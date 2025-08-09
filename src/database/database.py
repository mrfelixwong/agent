"""Database system for Meeting Agent - SQLite storage and retrieval"""

import sqlite3
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from pathlib import Path

from ..utils.logger import setup_logger
from ..utils.helpers import parse_meeting_json_fields, ensure_directory

logger = setup_logger(__name__)

class Database:
    """SQLite database manager for meeting data"""
    
    def __init__(self, db_path: str = "data/meetings.db"):
        self.db_path = Path(db_path)
        
        ensure_directory(self.db_path.parent)
        self._init_database()
    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_minutes INTEGER,
                    duration_seconds REAL DEFAULT 0.0,
                    start_time_minutes INTEGER DEFAULT 0,
                    audio_file_path TEXT,
                    transcript TEXT,
                    summary TEXT,
                    action_items TEXT,
                    status TEXT DEFAULT 'recorded',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create daily_summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    summary TEXT NOT NULL,  -- JSON summary data
                    total_meetings INTEGER DEFAULT 0,
                    total_duration INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_summaries_date ON daily_summaries(date)")
            
            conn.commit()
            
            # Run migrations to add new columns to existing databases
            self._run_migrations(conn)
    
    def _run_migrations(self, conn):
        """Run database migrations to add new columns"""
        cursor = conn.cursor()
        
        # Check if duration_seconds column exists
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'duration_seconds' not in columns:
            logger.info("Adding duration_seconds column to meetings table")
            cursor.execute("ALTER TABLE meetings ADD COLUMN duration_seconds REAL DEFAULT 0.0")
        
        if 'start_time_minutes' not in columns:
            logger.info("Adding start_time_minutes column to meetings table")
            cursor.execute("ALTER TABLE meetings ADD COLUMN start_time_minutes INTEGER DEFAULT 0")
        
        conn.commit()
    
    def save_meeting(
        self,
        name: str,
        audio_file_path: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """
        Save new meeting record
        
        Args:
            name: Meeting name
            audio_file_path: Path to audio recording file
            start_time: Meeting start time
            end_time: Meeting end time
            
        Returns:
            Meeting ID
        """
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            duration_minutes = None
            duration_seconds = 0.0
            start_time_minutes = 0
            
            current_start_time = start_time or datetime.now()
            
            if start_time and end_time:
                duration = end_time - start_time
                duration_minutes = int(duration.total_seconds() / 60)
                duration_seconds = duration.total_seconds()
            
            start_time_minutes = current_start_time.hour * 60 + current_start_time.minute
            
            cursor.execute("""
                INSERT INTO meetings (
                    name, date, start_time, end_time, duration_minutes, duration_seconds,
                    start_time_minutes, audio_file_path, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                current_start_time.date(),
                start_time,
                end_time,
                duration_minutes,
                duration_seconds,
                start_time_minutes,
                audio_file_path,
                'recorded'
            ))
            
            meeting_id = cursor.lastrowid
            conn.commit()
            return meeting_id
    
    def update_meeting_transcript(self, meeting_id: int, transcript: str) -> bool:
        """Update meeting transcript"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE meetings 
                SET transcript = ?, status = 'transcribed', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (transcript, meeting_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def update_meeting_summary(self, meeting_id: int, summary: Dict[str, Any]) -> bool:
        """Update meeting summary"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Extract action items for separate storage
            action_items = summary.get('action_items', [])
            
            cursor.execute("""
                UPDATE meetings 
                SET summary = ?, action_items = ?, status = 'summarized', 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(summary), json.dumps(action_items), meeting_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def update_meeting_duration(self, meeting_id: int, end_time: datetime, 
                               duration_minutes: int, duration_seconds: float) -> bool:
        """Update meeting with final end time and duration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE meetings 
                SET end_time = ?, duration_minutes = ?, duration_seconds = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (end_time, duration_minutes, duration_seconds, meeting_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def get_meeting(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
            row = cursor.fetchone()
            
            if row:
                meeting = dict(row)
                
                # Parse JSON fields
                return parse_meeting_json_fields(meeting)
            
            return None
    
    def get_meetings_by_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get all meetings for a specific date"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM meetings WHERE date = ? ORDER BY start_time",
                (target_date,)
            )
            
            meetings = []
            for row in cursor.fetchall():
                meeting = dict(row)
                
                # Parse JSON fields
                meeting = parse_meeting_json_fields(meeting)
                meetings.append(meeting)
            
            return meetings
    
    def get_meetings_by_date_range(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get meetings from the last N days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM meetings 
                WHERE date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC, start_time DESC
            """, (days_back,))
            
            meetings = []
            for row in cursor.fetchall():
                meeting = dict(row)
                meeting = parse_meeting_json_fields(meeting)
                meetings.append(meeting)
            
            return meetings
    
    def save_daily_summary(self, target_date: date, total_meetings: int, summary: str, key_themes: List[str]) -> bool:
        """Save or update daily summary"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create summary data structure
            summary_data = {
                'total_meetings': total_meetings,
                'daily_summary': summary,
                'key_themes': key_themes
            }
            
            # Insert or replace daily summary
            cursor.execute("""
                INSERT OR REPLACE INTO daily_summaries 
                (date, summary, total_meetings, total_duration)
                VALUES (?, ?, ?, ?)
            """, (
                target_date,
                json.dumps(summary_data),
                total_meetings,
                0  # duration field not used
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def get_daily_summary(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Get daily summary for date"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM daily_summaries WHERE date = ?",
                (target_date,)
            )
            
            row = cursor.fetchone()
            if row:
                daily_summary = dict(row)
                daily_summary['summary'] = json.loads(daily_summary['summary'])
                return daily_summary
            
            return None
    
    
    
    
    
    
    def close(self):
        """Close database connection (SQLite auto-closes, but for interface compatibility)"""
        pass