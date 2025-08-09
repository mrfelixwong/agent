"""
Database system for Meeting Agent
Handles meeting data storage and retrieval using SQLite
"""

import os
import sqlite3
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from pathlib import Path

from ..utils.logger import setup_logger
from ..utils.data_helpers import parse_meeting_json_fields
from ..utils.helpers import ensure_directory

logger = setup_logger(__name__)


class Database:
    """
    SQLite database manager for meeting data
    
    Stores meeting recordings, transcripts, summaries, and metadata
    in a local SQLite database with proper indexing and relationships.
    """
    
    def __init__(self, db_path: str = "data/meetings.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        
        # Ensure database directory exists
        ensure_directory(self.db_path.parent)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Database initialized at: {self.db_path}")
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create meetings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_minutes INTEGER,
                    participants TEXT,  -- JSON array
                    audio_file_path TEXT,
                    transcript TEXT,
                    summary TEXT,  -- JSON summary data
                    action_items TEXT,  -- JSON array
                    transcription_cost REAL DEFAULT 0.0,  -- Cost in USD
                    transcription_duration REAL DEFAULT 0.0,  -- Duration in seconds
                    status TEXT DEFAULT 'recorded',  -- recorded, transcribed, summarized, sent
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_summaries_date ON daily_summaries(date)")
            
            conn.commit()
            
            # Run migrations to add new columns to existing databases
            self._run_migrations(conn)
    
    def _run_migrations(self, conn):
        """Run database migrations to add new columns"""
        cursor = conn.cursor()
        
        # Check if transcription_cost column exists
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'transcription_cost' not in columns:
            logger.info("Adding transcription_cost column to meetings table")
            cursor.execute("ALTER TABLE meetings ADD COLUMN transcription_cost REAL DEFAULT 0.0")
        
        if 'transcription_duration' not in columns:
            logger.info("Adding transcription_duration column to meetings table")
            cursor.execute("ALTER TABLE meetings ADD COLUMN transcription_duration REAL DEFAULT 0.0")
        
        conn.commit()
    
    def save_meeting(
        self,
        name: str,
        participants: Optional[List[str]] = None,
        audio_file_path: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """
        Save new meeting record
        
        Args:
            name: Meeting name
            participants: List of participant names
            audio_file_path: Path to audio recording file
            start_time: Meeting start time
            end_time: Meeting end time
            
        Returns:
            Meeting ID
        """
        logger.debug(f"Saving meeting: {name} with {len(participants or [])} participants")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Calculate duration
            duration_minutes = None
            if start_time and end_time:
                duration = end_time - start_time
                duration_minutes = int(duration.total_seconds() / 60)
            
            # Insert meeting
            cursor.execute("""
                INSERT INTO meetings (
                    name, date, start_time, end_time, duration_minutes,
                    participants, audio_file_path, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                (start_time or datetime.now()).date(),
                start_time,
                end_time,
                duration_minutes,
                json.dumps(participants or []),
                audio_file_path,
                'recorded'
            ))
            
            meeting_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Meeting saved with ID: {meeting_id}")
            return meeting_id
    
    def update_meeting_transcript(self, meeting_id: int, transcript: str, 
                                 cost_info: Optional[Dict[str, float]] = None) -> bool:
        """Update meeting transcript with optional cost information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if cost_info:
                cursor.execute("""
                    UPDATE meetings 
                    SET transcript = ?, status = 'transcribed', 
                        transcription_cost = ?, transcription_duration = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (transcript, cost_info['total_cost'], 
                      cost_info['total_duration_seconds'], meeting_id))
            else:
                cursor.execute("""
                    UPDATE meetings 
                    SET transcript = ?, status = 'transcribed', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (transcript, meeting_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                logger.info(f"Transcript updated for meeting {meeting_id}")
                if cost_info:
                    logger.info(f"Transcription cost: ${cost_info['total_cost']:.4f}")
            
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
            
            if success:
                logger.info(f"Summary updated for meeting {meeting_id}")
            
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
    
    def get_meetings_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get meetings by processing status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM meetings WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
            
            meetings = []
            for row in cursor.fetchall():
                meeting = dict(row)
                
                # Parse JSON fields
                meeting = parse_meeting_json_fields(meeting)
                meetings.append(meeting)
            
            return meetings
    
    def mark_meeting_sent(self, meeting_id: int) -> bool:
        """Mark meeting as email sent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE meetings 
                SET status = 'sent', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (meeting_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            return success
    
    def save_daily_summary(self, target_date: date, summary: Dict[str, Any]) -> bool:
        """Save or update daily summary"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert or replace daily summary
            cursor.execute("""
                INSERT OR REPLACE INTO daily_summaries 
                (date, summary, total_meetings, total_duration)
                VALUES (?, ?, ?, ?)
            """, (
                target_date,
                json.dumps(summary),
                summary.get('total_meetings', 0),
                summary.get('total_duration', 0)
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                logger.info(f"Daily summary saved for {target_date}")
            
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
    
    def get_all_action_items(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get all action items from recent meetings"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, date, action_items 
                FROM meetings 
                WHERE date >= date('now', '-' || ? || ' days') 
                AND action_items IS NOT NULL 
                AND action_items != '[]'
                ORDER BY date DESC
            """, (days_back,))
            
            all_action_items = []
            for row in cursor.fetchall():
                meeting_data = dict(row)
                action_items = json.loads(meeting_data['action_items'] or '[]')
                
                for item in action_items:
                    item['meeting_name'] = meeting_data['name']
                    item['meeting_date'] = meeting_data['date']
                    item['meeting_id'] = meeting_data['id']
                    all_action_items.append(item)
            
            return all_action_items
    
    def search_meetings(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search meetings by name, transcript, or summary"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM meetings 
                WHERE name LIKE ? OR transcript LIKE ? OR summary LIKE ?
                ORDER BY date DESC
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            meetings = []
            for row in cursor.fetchall():
                meeting = dict(row)
                
                # Parse JSON fields
                meeting = parse_meeting_json_fields(meeting)
                meetings.append(meeting)
            
            return meetings
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total meetings
            cursor.execute("SELECT COUNT(*) FROM meetings")
            total_meetings = cursor.fetchone()[0]
            
            # Meetings by status
            cursor.execute("SELECT status, COUNT(*) FROM meetings GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # Total duration
            cursor.execute("SELECT SUM(duration_minutes) FROM meetings WHERE duration_minutes IS NOT NULL")
            total_duration = cursor.fetchone()[0] or 0
            
            # Recent activity (last 30 days)
            cursor.execute("SELECT COUNT(*) FROM meetings WHERE date >= date('now', '-30 days')")
            recent_meetings = cursor.fetchone()[0]
            
            return {
                'total_meetings': total_meetings,
                'status_breakdown': status_counts,
                'total_duration_minutes': total_duration,
                'recent_meetings_30_days': recent_meetings,
                'database_path': str(self.db_path),
                'database_size_bytes': os.path.getsize(self.db_path) if self.db_path.exists() else 0
            }
    
    def cleanup_old_meetings(self, days_to_keep: int = 90) -> int:
        """Remove old meetings beyond retention period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM meetings 
                WHERE date < date('now', '-' || ? || ' days')
            """, (days_to_keep,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old meetings")
            
            return deleted_count
    
    def close(self):
        """Close database connection (SQLite auto-closes, but for interface compatibility)"""
        logger.info("Database connection closed")


class MockDatabase(Database):
    """
    Mock database for testing without persistent storage
    """
    
    def __init__(self, **kwargs):
        """Initialize mock database with in-memory storage"""
        # Don't call parent __init__ to avoid file operations
        self.db_path = Path(":memory:")
        
        # In-memory data storage
        self._meetings = {}
        self._daily_summaries = {}
        self._next_meeting_id = 1
        
        # Mock settings
        self._simulate_error = False
        
        logger.info("Mock database initialized")
    
    def set_simulate_error(self, should_error: bool):
        """Set whether to simulate database errors"""
        self._simulate_error = should_error
    
    def save_meeting(
        self,
        name: str,
        participants: Optional[List[str]] = None,
        audio_file_path: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """Mock save meeting"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        meeting_id = self._next_meeting_id
        self._next_meeting_id += 1
        
        # Calculate duration
        duration_minutes = None
        if start_time and end_time:
            duration = end_time - start_time
            duration_minutes = int(duration.total_seconds() / 60)
        
        meeting = {
            'id': meeting_id,
            'name': name,
            'date': (start_time or datetime.now()).date(),
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': duration_minutes,
            'participants': participants or [],
            'audio_file_path': audio_file_path,
            'transcript': None,
            'summary': None,
            'action_items': [],
            'status': 'recorded',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self._meetings[meeting_id] = meeting
        return meeting_id
    
    def update_meeting_transcript(self, meeting_id: int, transcript: str, 
                                 cost_info: Optional[Dict[str, float]] = None) -> bool:
        """Mock update transcript with optional cost information"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        if meeting_id in self._meetings:
            self._meetings[meeting_id]['transcript'] = transcript
            self._meetings[meeting_id]['status'] = 'transcribed'
            self._meetings[meeting_id]['updated_at'] = datetime.now()
            
            # Add cost tracking if provided
            if cost_info:
                self._meetings[meeting_id]['transcription_cost'] = cost_info.get('total_cost', 0.0)
                self._meetings[meeting_id]['transcription_duration'] = cost_info.get('total_duration_seconds', 0.0)
            
            return True
        
        return False
    
    def update_meeting_summary(self, meeting_id: int, summary: Dict[str, Any]) -> bool:
        """Mock update summary"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        if meeting_id in self._meetings:
            self._meetings[meeting_id]['summary'] = summary
            self._meetings[meeting_id]['action_items'] = summary.get('action_items', [])
            self._meetings[meeting_id]['status'] = 'summarized'
            self._meetings[meeting_id]['updated_at'] = datetime.now()
            return True
        
        return False
    
    def get_meeting(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        """Mock get meeting"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        return self._meetings.get(meeting_id)
    
    def get_meetings_by_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Mock get meetings by date"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        return [
            meeting for meeting in self._meetings.values()
            if meeting['date'] == target_date
        ]
    
    def get_meetings_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Mock get meetings by status"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        return [
            meeting for meeting in self._meetings.values()
            if meeting['status'] == status
        ]
    
    def mark_meeting_sent(self, meeting_id: int) -> bool:
        """Mock mark meeting sent"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        if meeting_id in self._meetings:
            self._meetings[meeting_id]['status'] = 'sent'
            self._meetings[meeting_id]['updated_at'] = datetime.now()
            return True
        
        return False
    
    def save_daily_summary(self, target_date: date, summary: Dict[str, Any]) -> bool:
        """Mock save daily summary"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        self._daily_summaries[target_date] = {
            'date': target_date,
            'summary': summary,
            'total_meetings': summary.get('total_meetings', 0),
            'total_duration': summary.get('total_duration', 0),
            'created_at': datetime.now()
        }
        
        return True
    
    def get_daily_summary(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Mock get daily summary"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        return self._daily_summaries.get(target_date)
    
    def get_all_action_items(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Mock get all action items"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        all_items = []
        for meeting in self._meetings.values():
            if meeting.get('action_items'):
                for item in meeting['action_items']:
                    item_copy = item.copy()
                    item_copy['meeting_name'] = meeting['name']
                    item_copy['meeting_date'] = meeting['date']
                    item_copy['meeting_id'] = meeting['id']
                    all_items.append(item_copy)
        
        return all_items
    
    def search_meetings(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Mock search meetings"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        results = []
        query_lower = query.lower()
        
        for meeting in self._meetings.values():
            name_match = query_lower in meeting['name'].lower()
            transcript_match = meeting['transcript'] and query_lower in meeting['transcript'].lower()
            summary_match = meeting['summary'] and query_lower in str(meeting['summary']).lower()
            
            if name_match or transcript_match or summary_match:
                results.append(meeting)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Mock get statistics"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        total_meetings = len(self._meetings)
        status_counts = {}
        total_duration = 0
        
        for meeting in self._meetings.values():
            status = meeting['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            if meeting['duration_minutes']:
                total_duration += meeting['duration_minutes']
        
        return {
            'total_meetings': total_meetings,
            'status_breakdown': status_counts,
            'total_duration_minutes': total_duration,
            'recent_meetings_30_days': total_meetings,  # Mock: all meetings are recent
            'database_path': ':memory:',
            'database_size_bytes': 0
        }
    
    def cleanup_old_meetings(self, days_to_keep: int = 90) -> int:
        """Mock cleanup old meetings"""
        if self._simulate_error:
            raise Exception("Simulated database error")
        
        # Mock: no cleanup needed
        return 0
    
    def close(self):
        """Mock close connection"""
        pass