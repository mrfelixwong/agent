"""
Unit tests for database system
"""

import os
import tempfile
from datetime import datetime, date, timedelta
from pathlib import Path

# Import the components we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.database.database import Database, MockDatabase


class TestMockDatabase:
    """Test MockDatabase (no file dependencies)"""
    
    def test_mock_database_initialization(self):
        """Test mock database initialization"""
        db = MockDatabase()
        
        assert str(db.db_path) == ":memory:"
        assert db._next_meeting_id == 1
        assert len(db._meetings) == 0
        assert len(db._daily_summaries) == 0
        
    def test_mock_save_meeting(self):
        """Test mock meeting saving"""
        db = MockDatabase()
        
        start_time = datetime(2025, 1, 15, 14, 0)
        end_time = datetime(2025, 1, 15, 15, 30)
        
        meeting_id = db.save_meeting(
            name="Test Meeting",
            participants=["Alice", "Bob", "Charlie"],
            audio_file_path="/path/to/audio.wav",
            start_time=start_time,
            end_time=end_time
        )
        
        assert meeting_id == 1
        assert len(db._meetings) == 1
        
        meeting = db._meetings[meeting_id]
        assert meeting['name'] == "Test Meeting"
        assert meeting['participants'] == ["Alice", "Bob", "Charlie"]
        assert meeting['audio_file_path'] == "/path/to/audio.wav"
        assert meeting['duration_minutes'] == 90
        assert meeting['status'] == 'recorded'
        
    def test_mock_update_meeting_transcript(self):
        """Test mock transcript updating"""
        db = MockDatabase()
        
        meeting_id = db.save_meeting("Test Meeting")
        transcript = "This is the meeting transcript content."
        
        success = db.update_meeting_transcript(meeting_id, transcript)
        assert success is True
        
        meeting = db.get_meeting(meeting_id)
        assert meeting['transcript'] == transcript
        assert meeting['status'] == 'transcribed'
        
    def test_mock_update_meeting_summary(self):
        """Test mock summary updating"""
        db = MockDatabase()
        
        meeting_id = db.save_meeting("Test Meeting")
        summary = {
            'executive_summary': 'Meeting summary',
            'key_points': ['Point 1', 'Point 2'],
            'action_items': [
                {'task': 'Complete report', 'assignee': 'Alice', 'deadline': 'Friday'}
            ]
        }
        
        success = db.update_meeting_summary(meeting_id, summary)
        assert success is True
        
        meeting = db.get_meeting(meeting_id)
        assert meeting['summary'] == summary
        assert meeting['action_items'] == summary['action_items']
        assert meeting['status'] == 'summarized'
        
    def test_mock_get_meetings_by_date(self):
        """Test mock get meetings by date"""
        db = MockDatabase()
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Save meetings on different dates
        meeting1_id = db.save_meeting("Today's Meeting", start_time=datetime.combine(today, datetime.min.time()))
        meeting2_id = db.save_meeting("Yesterday's Meeting", start_time=datetime.combine(yesterday, datetime.min.time()))
        meeting3_id = db.save_meeting("Another Today Meeting", start_time=datetime.combine(today, datetime.min.time()))
        
        # Get today's meetings
        today_meetings = db.get_meetings_by_date(today)
        assert len(today_meetings) == 2
        meeting_names = [m['name'] for m in today_meetings]
        assert "Today's Meeting" in meeting_names
        assert "Another Today Meeting" in meeting_names
        
        # Get yesterday's meetings
        yesterday_meetings = db.get_meetings_by_date(yesterday)
        assert len(yesterday_meetings) == 1
        assert yesterday_meetings[0]['name'] == "Yesterday's Meeting"
        
    def test_mock_get_meetings_by_status(self):
        """Test mock get meetings by status"""
        db = MockDatabase()
        
        # Create meetings with different statuses
        meeting1_id = db.save_meeting("Meeting 1")
        meeting2_id = db.save_meeting("Meeting 2")
        meeting3_id = db.save_meeting("Meeting 3")
        
        # Update statuses
        db.update_meeting_transcript(meeting2_id, "transcript")
        db.update_meeting_summary(meeting3_id, {'summary': 'test'})
        
        # Test status queries
        recorded_meetings = db.get_meetings_by_status('recorded')
        transcribed_meetings = db.get_meetings_by_status('transcribed')
        summarized_meetings = db.get_meetings_by_status('summarized')
        
        assert len(recorded_meetings) == 1
        assert len(transcribed_meetings) == 1
        assert len(summarized_meetings) == 1
        
        assert recorded_meetings[0]['id'] == meeting1_id
        assert transcribed_meetings[0]['id'] == meeting2_id
        assert summarized_meetings[0]['id'] == meeting3_id
        
    def test_mock_daily_summary_operations(self):
        """Test mock daily summary save and retrieve"""
        db = MockDatabase()
        
        today = date.today()
        daily_summary = {
            'daily_summary': 'Productive day with 3 meetings',
            'total_meetings': 3,
            'total_duration': 180,
            'key_themes': ['Planning', 'Review']
        }
        
        # Save daily summary
        success = db.save_daily_summary(today, daily_summary)
        assert success is True
        
        # Retrieve daily summary
        retrieved = db.get_daily_summary(today)
        assert retrieved is not None
        assert retrieved['summary'] == daily_summary
        assert retrieved['total_meetings'] == 3
        assert retrieved['total_duration'] == 180
        
    def test_mock_action_items_aggregation(self):
        """Test mock action items aggregation"""
        db = MockDatabase()
        
        # Create meetings with action items
        meeting1_id = db.save_meeting("Meeting 1")
        meeting2_id = db.save_meeting("Meeting 2")
        
        summary1 = {
            'action_items': [
                {'task': 'Task 1', 'assignee': 'Alice'},
                {'task': 'Task 2', 'assignee': 'Bob'}
            ]
        }
        summary2 = {
            'action_items': [
                {'task': 'Task 3', 'assignee': 'Charlie'}
            ]
        }
        
        db.update_meeting_summary(meeting1_id, summary1)
        db.update_meeting_summary(meeting2_id, summary2)
        
        # Get all action items
        all_action_items = db.get_all_action_items()
        
        assert len(all_action_items) == 3
        tasks = [item['task'] for item in all_action_items]
        assert 'Task 1' in tasks
        assert 'Task 2' in tasks
        assert 'Task 3' in tasks
        
        # Check metadata is attached
        for item in all_action_items:
            assert 'meeting_name' in item
            assert 'meeting_date' in item
            assert 'meeting_id' in item
            
    def test_mock_search_meetings(self):
        """Test mock meeting search"""
        db = MockDatabase()
        
        # Create meetings with searchable content
        meeting1_id = db.save_meeting("Project Planning Meeting")
        meeting2_id = db.save_meeting("Budget Review")
        meeting3_id = db.save_meeting("Team Standup")
        
        # Add transcript to one meeting
        db.update_meeting_transcript(meeting2_id, "We discussed the budget allocation for Q4 projects")
        
        # Search by name
        results = db.search_meetings("Planning")
        assert len(results) == 1
        assert results[0]['name'] == "Project Planning Meeting"
        
        # Search by transcript
        results = db.search_meetings("budget")
        assert len(results) == 2  # "Budget Review" by name + meeting with "budget" in transcript
        
        # Search with no results
        results = db.search_meetings("nonexistent")
        assert len(results) == 0
        
    def test_mock_statistics(self):
        """Test mock statistics generation"""
        db = MockDatabase()
        
        # Create meetings with different statuses and durations
        meeting1_id = db.save_meeting("Meeting 1", start_time=datetime.now(), end_time=datetime.now() + timedelta(minutes=30))
        meeting2_id = db.save_meeting("Meeting 2", start_time=datetime.now(), end_time=datetime.now() + timedelta(minutes=45))
        
        db.update_meeting_transcript(meeting2_id, "transcript")
        
        stats = db.get_statistics()
        
        assert stats['total_meetings'] == 2
        assert stats['status_breakdown']['recorded'] == 1
        assert stats['status_breakdown']['transcribed'] == 1
        assert stats['total_duration_minutes'] == 75
        assert stats['recent_meetings_30_days'] == 2
        assert stats['database_path'] == ':memory:'
        
    def test_mock_error_simulation(self):
        """Test mock error simulation"""
        db = MockDatabase()
        db.set_simulate_error(True)
        
        # All operations should raise exceptions
        try:
            db.save_meeting("Test Meeting")
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Simulated database error" in str(e)
            
        try:
            db.get_statistics()
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Simulated database error" in str(e)
            
    def test_mock_mark_meeting_sent(self):
        """Test mock mark meeting as sent"""
        db = MockDatabase()
        
        meeting_id = db.save_meeting("Test Meeting")
        
        success = db.mark_meeting_sent(meeting_id)
        assert success is True
        
        meeting = db.get_meeting(meeting_id)
        assert meeting['status'] == 'sent'


class TestDatabaseWithRealSQLite:
    """Test Database with real SQLite operations"""
    
    def test_database_initialization(self):
        """Test database initialization creates tables"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(db_path)
            
            # Verify database file exists
            assert Path(db_path).exists()
            
            # Verify tables exist by attempting operations
            meeting_id = db.save_meeting("Test Meeting")
            assert meeting_id > 0
            
            db.close()
            
    def test_database_save_and_retrieve_meeting(self):
        """Test real database save and retrieve operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(db_path)
            
            start_time = datetime(2025, 1, 15, 14, 0)
            end_time = datetime(2025, 1, 15, 15, 30)
            
            meeting_id = db.save_meeting(
                name="Integration Test Meeting",
                participants=["Alice", "Bob"],
                audio_file_path="/path/to/audio.wav",
                start_time=start_time,
                end_time=end_time
            )
            
            # Retrieve meeting
            meeting = db.get_meeting(meeting_id)
            
            assert meeting is not None
            assert meeting['name'] == "Integration Test Meeting"
            assert meeting['participants'] == ["Alice", "Bob"]
            assert meeting['audio_file_path'] == "/path/to/audio.wav"
            assert meeting['duration_minutes'] == 90
            assert meeting['status'] == 'recorded'
            
            db.close()
            
    def test_database_transcript_and_summary_updates(self):
        """Test real database transcript and summary updates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(db_path)
            
            # Create meeting
            meeting_id = db.save_meeting("Test Meeting")
            
            # Update transcript
            transcript = "This is the meeting transcript with important discussions."
            success = db.update_meeting_transcript(meeting_id, transcript)
            assert success is True
            
            # Update summary
            summary = {
                'executive_summary': 'Important meeting summary',
                'key_points': ['Key point 1', 'Key point 2'],
                'action_items': [
                    {'task': 'Complete project', 'assignee': 'Alice', 'deadline': 'Friday', 'priority': 'high'}
                ]
            }
            success = db.update_meeting_summary(meeting_id, summary)
            assert success is True
            
            # Verify updates
            meeting = db.get_meeting(meeting_id)
            assert meeting['transcript'] == transcript
            assert meeting['summary'] == summary
            assert meeting['action_items'] == summary['action_items']
            assert meeting['status'] == 'summarized'
            
            db.close()
            
    def test_database_date_based_queries(self):
        """Test real database date-based queries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(db_path)
            
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # Create meetings on different dates
            meeting1_id = db.save_meeting(
                "Today's Meeting",
                start_time=datetime.combine(today, datetime.min.time())
            )
            meeting2_id = db.save_meeting(
                "Yesterday's Meeting",
                start_time=datetime.combine(yesterday, datetime.min.time())
            )
            
            # Test date filtering
            today_meetings = db.get_meetings_by_date(today)
            yesterday_meetings = db.get_meetings_by_date(yesterday)
            
            assert len(today_meetings) == 1
            assert len(yesterday_meetings) == 1
            assert today_meetings[0]['name'] == "Today's Meeting"
            assert yesterday_meetings[0]['name'] == "Yesterday's Meeting"
            
            db.close()
            
    def test_database_daily_summary_persistence(self):
        """Test real database daily summary persistence"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(db_path)
            
            today = date.today()
            daily_summary = {
                'daily_summary': 'Very productive day with strategic meetings',
                'total_meetings': 4,
                'total_duration': 240,
                'key_themes': ['Strategy', 'Planning', 'Execution'],
                'meeting_titles': ['Morning Standup', 'Client Call', 'Team Review', 'Planning Session']
            }
            
            # Save daily summary
            success = db.save_daily_summary(today, daily_summary)
            assert success is True
            
            # Retrieve daily summary
            retrieved = db.get_daily_summary(today)
            
            assert retrieved is not None
            assert retrieved['summary'] == daily_summary
            assert retrieved['total_meetings'] == 4
            assert retrieved['total_duration'] == 240
            
            db.close()
            
    def test_database_search_functionality(self):
        """Test real database search functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(db_path)
            
            # Create meetings with searchable content
            meeting1_id = db.save_meeting("Project Planning Meeting")
            meeting2_id = db.save_meeting("Budget Review Session")
            meeting3_id = db.save_meeting("Team Building Event")
            
            # Add transcripts
            db.update_meeting_transcript(meeting1_id, "We discussed the project roadmap and key milestones")
            db.update_meeting_transcript(meeting2_id, "Budget allocation for Q4 was reviewed in detail")
            
            # Search tests
            planning_results = db.search_meetings("Planning")
            budget_results = db.search_meetings("Budget")
            roadmap_results = db.search_meetings("roadmap")
            
            assert len(planning_results) == 1
            assert planning_results[0]['name'] == "Project Planning Meeting"
            
            assert len(budget_results) == 2  # Name match + transcript match
            
            assert len(roadmap_results) == 1
            assert roadmap_results[0]['name'] == "Project Planning Meeting"
            
            db.close()
            
    def test_database_statistics_accuracy(self):
        """Test real database statistics accuracy"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(db_path)
            
            # Create meetings with various properties
            meeting1_id = db.save_meeting("Meeting 1", start_time=datetime.now(), end_time=datetime.now() + timedelta(minutes=30))
            meeting2_id = db.save_meeting("Meeting 2", start_time=datetime.now(), end_time=datetime.now() + timedelta(minutes=60))
            meeting3_id = db.save_meeting("Meeting 3", start_time=datetime.now(), end_time=datetime.now() + timedelta(minutes=45))
            
            # Update statuses
            db.update_meeting_transcript(meeting2_id, "transcript")
            db.update_meeting_summary(meeting3_id, {'summary': 'test'})
            
            stats = db.get_statistics()
            
            assert stats['total_meetings'] == 3
            assert stats['status_breakdown']['recorded'] == 1
            assert stats['status_breakdown']['transcribed'] == 1
            assert stats['status_breakdown']['summarized'] == 1
            assert stats['total_duration_minutes'] == 135  # 30 + 60 + 45
            assert stats['recent_meetings_30_days'] == 3
            
            # Check database file size
            assert stats['database_size_bytes'] > 0
            
            db.close()


class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_complete_meeting_workflow(self):
        """Test complete meeting processing workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "workflow_test.db")
            db = Database(db_path)
            
            # Step 1: Save new meeting
            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=75)
            
            meeting_id = db.save_meeting(
                name="Complete Workflow Test",
                participants=["Alice", "Bob", "Charlie"],
                audio_file_path="/recordings/meeting.wav",
                start_time=start_time,
                end_time=end_time
            )
            
            # Verify initial state
            meeting = db.get_meeting(meeting_id)
            assert meeting['status'] == 'recorded'
            
            # Step 2: Add transcript
            transcript = "Complete meeting transcript with discussions about project progress, budget allocation, and next steps for the team."
            db.update_meeting_transcript(meeting_id, transcript)
            
            meeting = db.get_meeting(meeting_id)
            assert meeting['status'] == 'transcribed'
            assert meeting['transcript'] == transcript
            
            # Step 3: Add summary
            summary = {
                'executive_summary': 'Comprehensive project review with budget decisions',
                'key_points': [
                    'Project is on track for Q4 delivery',
                    'Budget increase approved for additional resources',
                    'New team members to be onboarded'
                ],
                'decisions_made': [
                    'Approved 15% budget increase',
                    'Hired 2 additional developers'
                ],
                'action_items': [
                    {'task': 'Onboard new developers', 'assignee': 'Alice', 'deadline': '2025-02-01', 'priority': 'high'},
                    {'task': 'Update project timeline', 'assignee': 'Bob', 'deadline': '2025-01-25', 'priority': 'medium'},
                    {'task': 'Prepare budget report', 'assignee': 'Charlie', 'deadline': '2025-01-30', 'priority': 'high'}
                ],
                'next_steps': [
                    'Schedule weekly check-ins with new team members',
                    'Review updated timeline with stakeholders'
                ]
            }
            
            db.update_meeting_summary(meeting_id, summary)
            
            meeting = db.get_meeting(meeting_id)
            assert meeting['status'] == 'summarized'
            assert meeting['summary'] == summary
            assert len(meeting['action_items']) == 3
            
            # Step 4: Mark as sent
            db.mark_meeting_sent(meeting_id)
            
            meeting = db.get_meeting(meeting_id)
            assert meeting['status'] == 'sent'
            
            # Step 5: Verify action items aggregation
            action_items = db.get_all_action_items()
            assert len(action_items) >= 3
            
            # Step 6: Create daily summary
            today = date.today()
            daily_summary_data = {
                'daily_summary': 'Highly productive day with strategic planning session',
                'total_meetings': 1,
                'total_duration': 75,
                'key_themes': ['Project Planning', 'Budget Management', 'Team Growth'],
                'meeting_titles': ['Complete Workflow Test']
            }
            
            db.save_daily_summary(today, daily_summary_data)
            daily_summary = db.get_daily_summary(today)
            
            assert daily_summary is not None
            assert daily_summary['summary']['total_meetings'] == 1
            
            # Step 7: Verify statistics
            stats = db.get_statistics()
            assert stats['total_meetings'] == 1
            assert stats['status_breakdown']['sent'] == 1
            assert stats['total_duration_minutes'] == 75
            
            db.close()
            
    def test_concurrent_operations_simulation(self):
        """Test database handling of concurrent-like operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "concurrent_test.db")
            db = Database(db_path)
            
            # Simulate multiple meetings being processed
            meeting_ids = []
            
            # Create multiple meetings rapidly
            for i in range(5):
                meeting_id = db.save_meeting(
                    f"Concurrent Meeting {i+1}",
                    participants=[f"User{j}" for j in range(i+1, i+4)],
                    start_time=datetime.now() + timedelta(hours=i),
                    end_time=datetime.now() + timedelta(hours=i, minutes=30)
                )
                meeting_ids.append(meeting_id)
            
            # Update all meetings with transcripts
            for meeting_id in meeting_ids:
                db.update_meeting_transcript(meeting_id, f"Transcript for meeting {meeting_id}")
            
            # Update all meetings with summaries
            for meeting_id in meeting_ids:
                summary = {
                    'executive_summary': f'Summary for meeting {meeting_id}',
                    'action_items': [
                        {'task': f'Task from meeting {meeting_id}', 'assignee': f'User{meeting_id}'}
                    ]
                }
                db.update_meeting_summary(meeting_id, summary)
            
            # Verify all operations completed successfully
            for meeting_id in meeting_ids:
                meeting = db.get_meeting(meeting_id)
                assert meeting is not None
                assert meeting['status'] == 'summarized'
                assert meeting['transcript'] is not None
                assert meeting['summary'] is not None
            
            # Verify aggregated data
            stats = db.get_statistics()
            assert stats['total_meetings'] == 5
            assert stats['status_breakdown']['summarized'] == 5
            
            action_items = db.get_all_action_items()
            assert len(action_items) == 5
            
            db.close()


def run_database_tests():
    """Run all database tests"""
    print("🗄️ Testing Database System...")
    
    test_classes = [
        TestMockDatabase,
        TestDatabaseWithRealSQLite,
        TestDatabaseIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\n  Testing {class_name}:")
        
        instance = test_class()
        test_methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                getattr(instance, test_method)()
                print(f"    ✅ {test_method}")
                passed_tests += 1
            except Exception as e:
                print(f"    ❌ {test_method}: {e}")
    
    print(f"\n📊 Database Tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_database_tests()
    exit(0 if success else 1)