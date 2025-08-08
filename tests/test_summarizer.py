"""
Unit tests for AI summarization system
"""

import os
import time
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime

# Import the components we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.ai.summarizer import Summarizer, MockSummarizer


class TestMockSummarizer:
    """Test MockSummarizer (no API dependencies)"""
    
    def test_mock_summarizer_initialization(self):
        """Test mock summarizer initialization"""
        summarizer = MockSummarizer(model="test-model", max_tokens=2000)
        
        assert summarizer.model == "test-model"
        assert summarizer.max_tokens == 2000
        
    def test_mock_summarizer_default_initialization(self):
        """Test mock summarizer with default values"""
        summarizer = MockSummarizer()
        
        assert summarizer.model == "mock-gpt-4"
        assert summarizer.max_tokens == 1500
        
    def test_mock_meeting_summarization(self):
        """Test mock meeting summary generation"""
        summarizer = MockSummarizer()
        
        transcript = "This is a test meeting transcript with important discussions about project planning."
        
        summary = summarizer.summarize_meeting(
            transcript=transcript,
            meeting_name="Test Meeting",
            participants=["Alice", "Bob"],
            duration_minutes=60
        )
        
        # Check structure
        assert 'executive_summary' in summary
        assert 'key_points' in summary
        assert 'decisions_made' in summary
        assert 'action_items' in summary
        assert 'next_steps' in summary
        
        # Check metadata
        assert summary['meeting_name'] == "Test Meeting"
        assert summary['participants'] == ["Alice", "Bob"]
        assert summary['duration_minutes'] == 60
        assert summary['transcript_length'] == len(transcript)
        assert 'summary_generated_at' in summary
        assert summary['model_used'] == "mock-gpt-4"
        
    def test_mock_summarization_empty_transcript(self):
        """Test mock summarization with empty transcript"""
        summarizer = MockSummarizer()
        
        try:
            summarizer.summarize_meeting("")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Transcript cannot be empty" in str(e)
            
    def test_mock_action_item_extraction(self):
        """Test mock action item extraction"""
        summarizer = MockSummarizer()
        
        transcript = "John needs to review the proposal by Friday. Sarah should update the budget."
        action_items = summarizer.extract_action_items(transcript)
        
        assert isinstance(action_items, list)
        assert len(action_items) > 0
        
        # Check action item structure
        for item in action_items:
            assert 'task' in item
            assert 'assignee' in item
            assert 'deadline' in item
            assert 'priority' in item
            
    def test_mock_action_items_empty_transcript(self):
        """Test mock action item extraction with empty transcript"""
        summarizer = MockSummarizer()
        
        action_items = summarizer.extract_action_items("")
        assert action_items == []
        
    def test_mock_daily_summary_generation(self):
        """Test mock daily summary generation"""
        summarizer = MockSummarizer()
        
        meeting_summaries = [
            {
                'meeting_name': 'Morning Standup',
                'duration_minutes': 30,
                'key_points': ['Sprint progress', 'Blockers discussion'],
                'action_items': [{'task': 'Fix bug #123', 'assignee': 'Dev Team'}]
            },
            {
                'meeting_name': 'Client Call',
                'duration_minutes': 45,
                'key_points': ['Requirements review', 'Timeline discussion'],
                'action_items': [{'task': 'Update proposal', 'assignee': 'PM'}]
            }
        ]
        
        daily_summary = summarizer.generate_daily_summary(meeting_summaries)
        
        # Check structure
        assert 'daily_summary' in daily_summary
        assert 'total_meetings' in daily_summary
        assert 'total_duration' in daily_summary
        assert 'key_themes' in daily_summary
        assert 'all_action_items' in daily_summary
        assert 'meeting_titles' in daily_summary
        
        # Check values
        assert daily_summary['total_meetings'] == 2
        assert daily_summary['total_duration'] == 75
        assert len(daily_summary['meeting_titles']) == 2
        
    def test_mock_daily_summary_no_meetings(self):
        """Test mock daily summary with no meetings"""
        summarizer = MockSummarizer()
        
        daily_summary = summarizer.generate_daily_summary([])
        
        assert daily_summary['daily_summary'] == 'No meetings recorded today.'
        assert daily_summary['total_meetings'] == 0
        assert daily_summary['total_duration'] == 0
        assert daily_summary['key_themes'] == []
        assert daily_summary['all_action_items'] == []
        
    def test_mock_custom_settings(self):
        """Test mock summarizer with custom settings"""
        custom_summary = {
            'executive_summary': 'Custom executive summary',
            'key_points': ['Custom point 1', 'Custom point 2']
        }
        custom_action_items = [
            {'task': 'Custom task', 'assignee': 'Custom assignee', 'deadline': 'Tomorrow', 'priority': 'high'}
        ]
        
        summarizer = MockSummarizer()
        summarizer.set_mock_summary(custom_summary)
        summarizer.set_mock_action_items(custom_action_items)
        summarizer.set_processing_delay(0.05)
        
        transcript = "Test transcript"
        
        # Test custom summary
        start_time = time.time()
        summary = summarizer.summarize_meeting(transcript)
        duration = time.time() - start_time
        
        assert summary['executive_summary'] == 'Custom executive summary'
        assert 'Custom point 1' in summary['key_points']
        assert duration >= 0.05  # Check delay was applied
        
        # Test custom action items
        action_items = summarizer.extract_action_items(transcript)
        assert len(action_items) == 1
        assert action_items[0]['task'] == 'Custom task'
        
    def test_mock_error_simulation(self):
        """Test mock error simulation"""
        summarizer = MockSummarizer()
        summarizer.set_simulate_error(True)
        
        transcript = "Test transcript"
        
        # Test summarization error
        try:
            summarizer.summarize_meeting(transcript)
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Simulated summarization error" in str(e)
            
        # Test action item extraction error
        try:
            summarizer.extract_action_items(transcript)
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Simulated action item extraction error" in str(e)
            
        # Test daily summary error
        try:
            summarizer.generate_daily_summary([])
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Simulated daily summary error" in str(e)


class TestSummarizerWithMocks:
    """Test Summarizer with mocked OpenAI API"""
    
    def test_summarizer_init_no_openai(self):
        """Test Summarizer when OpenAI package is not available"""
        with patch('src.ai.summarizer.openai', None):
            try:
                summarizer = Summarizer(api_key="test_key")
                assert False, "Should have raised ImportError"
            except ImportError as e:
                assert "OpenAI package is not installed" in str(e)
                
    def test_summarizer_init_no_api_key(self):
        """Test Summarizer when no API key is provided"""
        mock_openai = MagicMock()
        
        with patch('src.ai.summarizer.openai', mock_openai):
            with patch.dict(os.environ, {}, clear=True):
                try:
                    summarizer = Summarizer()
                    assert False, "Should have raised ValueError"
                except ValueError as e:
                    assert "OpenAI API key required" in str(e)
                    
    def test_summarizer_successful_init(self):
        """Test successful Summarizer initialization"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        with patch('src.ai.summarizer.openai', mock_openai):
            summarizer = Summarizer(api_key="test_key", model="gpt-3.5-turbo")
            
            assert summarizer.model == "gpt-3.5-turbo"
            assert summarizer.max_tokens == 1500
            mock_openai.OpenAI.assert_called_once_with(api_key="test_key")
            
    def test_summarizer_with_env_api_key(self):
        """Test Summarizer initialization with environment API key"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        with patch('src.ai.summarizer.openai', mock_openai):
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'env_test_key'}):
                summarizer = Summarizer(max_tokens=2000)
                
                assert summarizer.max_tokens == 2000
                mock_openai.OpenAI.assert_called_once_with()
                
    def test_mocked_meeting_summarization(self):
        """Test meeting summarization with mocked API"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """
        EXECUTIVE SUMMARY
        This was a productive project planning meeting focusing on Q4 deliverables.
        
        KEY POINTS
        - Reviewed current project status and milestones
        - Discussed resource allocation for upcoming sprint
        - Addressed potential risks and mitigation strategies
        
        DECISIONS MADE
        - Approved additional budget for development tools
        - Set final delivery date for December 20th
        
        ACTION ITEMS
        - John to create detailed project timeline
        - Sarah to coordinate with vendor team
        
        NEXT STEPS
        - Schedule weekly check-ins starting Monday
        - Prepare status report for stakeholders
        """
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('src.ai.summarizer.openai', mock_openai):
            summarizer = Summarizer(api_key="test_key")
            
            transcript = "We discussed the project timeline and budget allocation..."
            summary = summarizer.summarize_meeting(
                transcript=transcript,
                meeting_name="Project Planning",
                participants=["John", "Sarah"],
                duration_minutes=45
            )
            
            # Check API was called
            mock_client.chat.completions.create.assert_called()
            
            # Check summary structure
            assert 'executive_summary' in summary
            assert 'key_points' in summary
            assert 'decisions_made' in summary
            assert 'action_items' in summary
            assert 'next_steps' in summary
            
            # Check metadata
            assert summary['meeting_name'] == "Project Planning"
            assert summary['participants'] == ["John", "Sarah"]
            assert summary['duration_minutes'] == 45
            
    def test_mocked_action_item_extraction(self):
        """Test action item extraction with mocked API"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        # Mock JSON response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''[
            {
                "task": "Review project proposal",
                "assignee": "John",
                "deadline": "End of week",
                "priority": "high"
            },
            {
                "task": "Update budget spreadsheet",
                "assignee": "Sarah",
                "deadline": "Next Tuesday",
                "priority": "medium"
            }
        ]'''
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('src.ai.summarizer.openai', mock_openai):
            summarizer = Summarizer(api_key="test_key")
            
            transcript = "John needs to review the proposal. Sarah should update the budget."
            action_items = summarizer.extract_action_items(transcript)
            
            assert len(action_items) == 2
            assert action_items[0]['task'] == "Review project proposal"
            assert action_items[0]['assignee'] == "John"
            assert action_items[1]['priority'] == "medium"
            
    def test_mocked_daily_summary(self):
        """Test daily summary generation with mocked API"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        # Mock responses for theme extraction and daily summary
        mock_responses = [
            "Project Planning\nBudget Review\nTeam Coordination",  # Themes
            "Today was highly productive with 2 important meetings covering project planning and budget review. Key decisions were made regarding resource allocation and timeline adjustments."  # Daily summary
        ]
        
        mock_response_objs = []
        for content in mock_responses:
            mock_resp = MagicMock()
            mock_resp.choices[0].message.content = content
            mock_response_objs.append(mock_resp)
        
        mock_client.chat.completions.create.side_effect = mock_response_objs
        
        with patch('src.ai.summarizer.openai', mock_openai):
            summarizer = Summarizer(api_key="test_key")
            
            meeting_summaries = [
                {
                    'meeting_name': 'Morning Standup',
                    'duration_minutes': 30,
                    'key_points': ['Sprint progress', 'Blockers'],
                },
                {
                    'meeting_name': 'Budget Review',
                    'duration_minutes': 60,
                    'key_points': ['Q4 budget', 'Resource allocation'],
                }
            ]
            
            daily_summary = summarizer.generate_daily_summary(meeting_summaries)
            
            assert daily_summary['total_meetings'] == 2
            assert daily_summary['total_duration'] == 90
            assert len(daily_summary['key_themes']) > 0
            assert 'Today was highly productive' in daily_summary['daily_summary']
            
    def test_summarization_error_handling(self):
        """Test error handling in summarization"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('src.ai.summarizer.openai', mock_openai):
            summarizer = Summarizer(api_key="test_key")
            
            try:
                summarizer.summarize_meeting("Test transcript")
                assert False, "Should have raised exception"
            except Exception as e:
                assert "API Error" in str(e)


class TestSummarizerIntegration:
    """Integration tests for summarization system"""
    
    def test_summary_parsing(self):
        """Test summary response parsing"""
        summarizer = MockSummarizer()
        
        # Test with various transcript formats
        transcripts = [
            "Short meeting about project status.",
            "Long meeting transcript with multiple discussion points about budget, timeline, resources, and deliverables. The team discussed various options and made several important decisions.",
            ""  # This should raise an error
        ]
        
        for i, transcript in enumerate(transcripts[:2]):  # Skip empty transcript
            summary = summarizer.summarize_meeting(
                transcript=transcript,
                meeting_name=f"Test Meeting {i+1}"
            )
            
            # Check that all required sections are present
            required_sections = ['executive_summary', 'key_points', 'decisions_made', 'action_items', 'next_steps']
            for section in required_sections:
                assert section in summary
                
    def test_metadata_preservation(self):
        """Test that metadata is properly preserved in summaries"""
        summarizer = MockSummarizer()
        
        participants = ["Alice Smith", "Bob Johnson", "Carol Davis"]
        meeting_name = "Q4 Planning Session"
        duration = 90
        
        transcript = "Detailed discussion about Q4 planning and resource allocation."
        
        summary = summarizer.summarize_meeting(
            transcript=transcript,
            meeting_name=meeting_name,
            participants=participants,
            duration_minutes=duration
        )
        
        assert summary['meeting_name'] == meeting_name
        assert summary['participants'] == participants
        assert summary['duration_minutes'] == duration
        assert summary['transcript_length'] == len(transcript)
        assert summary['model_used'] == "mock-gpt-4"
        
        # Check timestamp format
        timestamp = summary['summary_generated_at']
        datetime.fromisoformat(timestamp)  # Should not raise exception
        
    def test_action_item_aggregation(self):
        """Test action item aggregation in daily summaries"""
        summarizer = MockSummarizer()
        
        # Set custom action items for predictable testing
        test_action_items = [
            {'task': 'Review proposal', 'assignee': 'John', 'deadline': 'Friday', 'priority': 'high'}
        ]
        summarizer.set_mock_action_items(test_action_items)
        
        meeting_summaries = [
            {'meeting_name': 'Meeting 1', 'duration_minutes': 30},
            {'meeting_name': 'Meeting 2', 'duration_minutes': 45}
        ]
        
        daily_summary = summarizer.generate_daily_summary(meeting_summaries)
        
        # Should have action items from both meetings
        expected_action_count = len(test_action_items) * len(meeting_summaries)
        assert len(daily_summary['all_action_items']) == expected_action_count
        
    def test_performance_timing(self):
        """Test that mock processing delays work correctly"""
        summarizer = MockSummarizer()
        summarizer.set_processing_delay(0.1)
        
        transcript = "Test meeting transcript"
        
        # Test summarization timing
        start_time = time.time()
        summarizer.summarize_meeting(transcript)
        duration = time.time() - start_time
        assert duration >= 0.1
        
        # Test action item extraction timing
        start_time = time.time()
        summarizer.extract_action_items(transcript)
        duration = time.time() - start_time
        assert duration >= 0.1


def run_summarization_tests():
    """Run all summarization tests"""
    print("🤖 Testing AI Summarization System...")
    
    test_classes = [
        TestMockSummarizer,
        TestSummarizerWithMocks,
        TestSummarizerIntegration
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
    
    print(f"\n📊 Summarization Tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_summarization_tests()
    exit(0 if success else 1)