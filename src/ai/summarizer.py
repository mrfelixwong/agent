"""
AI summarization system using OpenAI GPT
Handles meeting transcript analysis and summary generation
"""

import os
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None

from ..utils.logger import setup_logger, log_performance

logger = setup_logger(__name__)


class Summarizer:
    """
    AI-powered meeting summarizer using OpenAI GPT
    
    Analyzes meeting transcripts and generates structured summaries
    with key points, action items, and participant insights.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = "gpt-4",
        max_tokens: int = 1500
    ):
        """
        Initialize summarizer
        
        Args:
            api_key: OpenAI API key (optional, can use environment variable)
            model: GPT model to use for summarization
            max_tokens: Maximum tokens for summary response
        """
        self.model = model
        self.max_tokens = max_tokens
        
        # Initialize OpenAI client
        if openai is None:
            raise ImportError(
                "OpenAI package is not installed. Please install with: pip install openai"
            )
        
        # Set up API key
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        elif os.getenv('OPENAI_API_KEY'):
            self.client = openai.OpenAI()
        else:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        logger.info(f"Summarizer initialized with model: {model}")
    
    @log_performance
    def summarize_meeting(
        self, 
        transcript: str, 
        meeting_name: Optional[str] = None,
        duration_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive meeting summary from transcript
        
        Args:
            transcript: Full meeting transcript text
            meeting_name: Name/title of the meeting (optional)
            duration_minutes: Meeting duration in minutes (optional)
            
        Returns:
            Dictionary containing structured summary data
        """
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")
        
        try:
            # Prepare context information
            context_info = []
            if meeting_name:
                context_info.append(f"Meeting: {meeting_name}")
            if duration_minutes:
                context_info.append(f"Duration: {duration_minutes} minutes")
            
            context = "\n".join(context_info) if context_info else ""
            
            # Create summarization prompt
            prompt = self._create_summary_prompt(transcript, context)
            
            # Generate summary using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert meeting analyst. Generate comprehensive, structured summaries of meeting transcripts."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            summary_text = response.choices[0].message.content
            
            # Parse the structured response
            summary = self._parse_summary_response(summary_text)
            
            # Add metadata
            summary.update({
                'meeting_name': meeting_name,
                'duration_minutes': duration_minutes,
                'transcript_length': len(transcript),
                'summary_generated_at': datetime.now().isoformat(),
                'model_used': self.model
            })
            
            logger.info(f"Meeting summary generated successfully ({len(summary_text)} chars)")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate meeting summary: {e}")
            raise
    
    def extract_action_items(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Extract action items from meeting transcript
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            List of action item dictionaries
        """
        if not transcript or not transcript.strip():
            return []
        
        try:
            prompt = f"""
            Analyze the following meeting transcript and extract all action items.
            For each action item, identify:
            - The specific task or action
            - Who is responsible (if mentioned)
            - Any deadline or timeframe (if mentioned)
            - Priority level (high/medium/low based on context)
            
            Format as JSON array with objects containing: task, assignee, deadline, priority
            
            Transcript:
            {transcript}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting action items from meeting transcripts. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            # Parse JSON response
            import json
            action_items = json.loads(response.choices[0].message.content)
            
            logger.info(f"Extracted {len(action_items)} action items")
            return action_items
            
        except Exception as e:
            logger.error(f"Failed to extract action items: {e}")
            return []
    
    def generate_daily_summary(self, meeting_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate daily summary from multiple meeting summaries
        
        Args:
            meeting_summaries: List of individual meeting summary dictionaries
            
        Returns:
            Dictionary containing daily summary
        """
        if not meeting_summaries:
            return {
                'daily_summary': 'No meetings recorded today.',
                'total_meetings': 0,
                'total_duration': 0,
                'key_themes': [],
                'all_action_items': [],
                'summary_generated_at': datetime.now().isoformat()
            }
        
        try:
            # Aggregate information
            total_meetings = len(meeting_summaries)
            total_duration = sum(
                summary.get('duration_minutes', 0) 
                for summary in meeting_summaries
            )
            
            # Collect all summaries and action items
            meeting_texts = []
            all_action_items = []
            
            for i, summary in enumerate(meeting_summaries, 1):
                meeting_name = summary.get('meeting_name', f'Meeting {i}')
                key_points = summary.get('key_points', [])
                action_items = summary.get('action_items', [])
                
                meeting_text = f"""
                Meeting {i}: {meeting_name}
                Duration: {summary.get('duration_minutes', 'Unknown')} minutes
                Key Points: {'; '.join(key_points) if key_points else 'None recorded'}
                """
                meeting_texts.append(meeting_text)
                all_action_items.extend(action_items)
            
            # Generate comprehensive daily summary
            prompt = f"""
            Create a comprehensive daily summary for {total_meetings} meetings held today.
            
            Meetings Overview:
            {''.join(meeting_texts)}
            
            Please provide:
            1. A brief overview of the day's meetings
            2. Key themes and topics that emerged across meetings
            3. Major decisions or outcomes
            4. Overall productivity assessment
            
            Keep it concise but comprehensive (2-3 paragraphs).
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an executive assistant creating daily meeting summaries. Be concise and focus on key insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600,
                temperature=0.4
            )
            
            daily_summary_text = response.choices[0].message.content
            
            # Extract key themes
            themes = self._extract_key_themes(meeting_summaries)
            
            daily_summary = {
                'daily_summary': daily_summary_text,
                'total_meetings': total_meetings,
                'total_duration': total_duration,
                'key_themes': themes,
                'all_action_items': all_action_items,
                'meeting_titles': [
                    summary.get('meeting_name', f'Meeting {i}') 
                    for i, summary in enumerate(meeting_summaries, 1)
                ],
                'summary_generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"Daily summary generated for {total_meetings} meetings")
            return daily_summary
            
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {e}")
            raise
    
    def _create_summary_prompt(self, transcript: str, context: str = "") -> str:
        """Create summarization prompt for GPT"""
        prompt = f"""
        Please analyze the following meeting transcript and provide a comprehensive summary.
        
        {context}
        
        Please structure your response with the following sections:
        
        1. EXECUTIVE SUMMARY (2-3 sentences)
        2. KEY POINTS (bullet points of main discussion topics)
        3. DECISIONS MADE (specific decisions or resolutions)
        4. ACTION ITEMS (tasks assigned with responsible parties if mentioned)
        5. NEXT STEPS (follow-up actions or future meetings)
        
        Transcript:
        {transcript}
        
        Provide a clear, structured summary that captures the essential information from this meeting.
        """
        return prompt
    
    def _parse_summary_response(self, summary_text: str) -> Dict[str, Any]:
        """Parse structured summary response from GPT"""
        try:
            # Simple parsing - look for section headers
            sections = {
                'executive_summary': '',
                'key_points': [],
                'decisions_made': [],
                'action_items': [],
                'next_steps': []
            }
            
            current_section = None
            lines = summary_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers
                line_upper = line.upper()
                if 'EXECUTIVE SUMMARY' in line_upper:
                    current_section = 'executive_summary'
                    continue
                elif 'KEY POINTS' in line_upper:
                    current_section = 'key_points'
                    continue
                elif 'DECISIONS MADE' in line_upper or 'DECISIONS' in line_upper:
                    current_section = 'decisions_made'
                    continue
                elif 'ACTION ITEMS' in line_upper:
                    current_section = 'action_items'
                    continue
                elif 'NEXT STEPS' in line_upper:
                    current_section = 'next_steps'
                    continue
                
                # Add content to current section
                if current_section == 'executive_summary':
                    sections['executive_summary'] += line + ' '
                elif current_section in ['key_points', 'decisions_made', 'action_items', 'next_steps']:
                    if line.startswith('- ') or line.startswith('• '):
                        sections[current_section].append(line[2:].strip())
                    elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                        sections[current_section].append(line[3:].strip())
                    else:
                        sections[current_section].append(line)
            
            # Clean up executive summary
            sections['executive_summary'] = sections['executive_summary'].strip()
            
            return sections
            
        except Exception as e:
            logger.warning(f"Failed to parse structured summary: {e}")
            # Fallback: return raw summary
            return {
                'executive_summary': summary_text,
                'key_points': [],
                'decisions_made': [],
                'action_items': [],
                'next_steps': []
            }
    
    def _extract_key_themes(self, meeting_summaries: List[Dict[str, Any]]) -> List[str]:
        """Extract key themes across multiple meetings"""
        try:
            # Collect all key points from meetings
            all_points = []
            for summary in meeting_summaries:
                points = summary.get('key_points', [])
                all_points.extend(points)
            
            if not all_points:
                return []
            
            # Use AI to identify common themes
            points_text = '\n'.join(f"- {point}" for point in all_points[:20])  # Limit for token usage
            
            prompt = f"""
            Analyze the following key points from today's meetings and identify 3-5 major themes or topics.
            Return only the theme names, one per line.
            
            Key Points:
            {points_text}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You identify key themes from meeting content. Return only theme names, one per line."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            themes = [
                line.strip().replace('- ', '') 
                for line in response.choices[0].message.content.split('\n') 
                if line.strip()
            ]
            
            return themes[:5]  # Return max 5 themes
            
        except Exception as e:
            logger.warning(f"Failed to extract key themes: {e}")
            return []


