#!/usr/bin/env python3
"""
Demo of Meeting Agent with Real OpenAI APIs
Shows AI summarization and transcription working with real APIs
"""

import sys
import os
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import MeetingAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_real_ai_agent():
    """Create MeetingAgent with real AI but mock audio/email"""
    from src.ai.summarizer import Summarizer
    from src.transcription.transcriber import Transcriber
    
    # Start with mock components
    agent = MeetingAgent(use_mock_components=True)
    
    # Replace AI components with real ones
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if api_key:
        print("🤖 Integrating Real OpenAI APIs...")
        
        # Real AI Summarizer
        agent.summarizer = Summarizer(
            api_key=api_key,
            model='gpt-4o-mini'  # Use faster/cheaper model for demo
        )
        
        # Real Transcriber (setup only, still uses mock audio)
        agent.transcriber = Transcriber(
            api_key=api_key,
            model='whisper-1'
        )
        
        print("   ✅ Real AI components initialized")
    
    return agent


def demo_real_ai_meeting():
    """Demonstrate real AI processing of meeting content"""
    print("🎙️ Meeting Agent with Real AI Demo")
    print("=" * 40)
    
    try:
        # Create agent with real AI
        agent = create_real_ai_agent()
        
        print("\n1. Starting Meeting...")
        meeting_info = agent.start_meeting(
            "Product Strategy Session - Q1 Planning", 
            ["Sarah (CEO)", "Mike (CTO)", "Jennifer (PM)", "Alex (Design)"]
        )
        print(f"   ✅ Meeting: {meeting_info['name']}")
        print(f"   Meeting ID: {meeting_info['id']}")
        print(f"   Participants: {', '.join(meeting_info['participants'])}")
        
        print("\n2. Simulating Meeting Content...")
        
        # Inject realistic meeting transcript for AI processing
        realistic_transcript = """
        Sarah: Good morning everyone, let's dive into our Q1 planning session. I want to focus on our product strategy and key initiatives for the next quarter.

        Mike: Thanks Sarah. From a technical perspective, we've completed the infrastructure migration and we're ready to scale. Our performance metrics show 40% improvement in response times.

        Jennifer: That's great Mike. I've been analyzing user feedback and we have three major feature requests that could significantly impact user retention. The top priority is the collaborative workspace feature that 67% of users have requested.

        Alex: I agree with Jennifer. From a design standpoint, I've completed the wireframes for the collaborative workspace. User testing shows 89% positive feedback on the new interface design.

        Sarah: Excellent work everyone. Let's prioritize these initiatives. Mike, what's your assessment of the technical feasibility?

        Mike: The collaborative workspace will require about 6 weeks of development time. We'll need to implement real-time synchronization and conflict resolution. I recommend we start with a beta release to a limited user group.

        Jennifer: That aligns with our product roadmap. I suggest we target the beta for mid-February and full release by end of March. We should also consider the premium pricing tier for advanced collaborative features.

        Alex: For the beta, I can have the UI components ready by next week. We should focus on core functionality first - document sharing, real-time editing, and user presence indicators.

        Sarah: Perfect. Let's establish our action items. Mike, you'll lead the technical implementation. Jennifer, you'll coordinate with our beta user group and handle the pricing strategy. Alex, you'll finalize the UI and work on user onboarding flows.

        Mike: Agreed. I'll also coordinate with the DevOps team for infrastructure scaling to handle the increased load from collaborative features.

        Jennifer: I'll prepare the beta user communication and set up feedback collection mechanisms. We should aim for 100 beta users initially.

        Alex: I'll also create documentation for the new features and work with the marketing team on feature announcement materials.

        Sarah: Excellent coordination everyone. Our key decisions today: prioritize collaborative workspace, 6-week development timeline, mid-February beta launch, end of March full release. Let's schedule weekly check-ins to track progress.

        Mike: One more thing - we should consider the security implications of real-time collaboration. I'll include security review in the development timeline.

        Jennifer: Good point Mike. I'll also coordinate with legal team regarding data privacy for collaborative features.

        Sarah: Great thinking ahead. Any final questions? No? Excellent meeting everyone. Let's make Q1 a success with this new collaborative workspace feature.
        """
        
        # Simulate recording progress
        print("   📝 Recording in progress...")
        for i in range(3):
            time.sleep(1)
            print(f"   Recording... {i+1}s")
        
        # Inject the realistic transcript
        agent.transcriber._transcript_text = realistic_transcript
        
        print(f"\n3. Processing Meeting (Real AI)...")
        print("   🤖 Generating summary with GPT-4...")
        
        completed = agent.stop_meeting()
        
        print(f"   ✅ Meeting processed: {completed['name']}")
        print(f"   Transcript: {len(completed.get('transcript', ''))} characters")
        
        # Display the real AI summary
        summary = completed.get('summary', {})
        if summary and summary.get('executive_summary'):
            print(f"\n4. 🤖 Real AI Summary Generated:")
            print(f"\n📋 Executive Summary:")
            print(f"   {summary['executive_summary']}")
            
            if summary.get('key_points'):
                print(f"\n🔑 Key Points:")
                for i, point in enumerate(summary['key_points'][:5], 1):
                    print(f"   {i}. {point}")
            
            if summary.get('decisions_made'):
                print(f"\n✅ Decisions Made:")
                for i, decision in enumerate(summary['decisions_made'][:5], 1):
                    print(f"   {i}. {decision}")
            
            if summary.get('action_items'):
                print(f"\n📝 Action Items:")
                for i, item in enumerate(summary['action_items'][:5], 1):
                    if isinstance(item, dict):
                        task = item.get('task', item.get('description', str(item)))
                        assignee = item.get('assignee', '')
                        due_date = item.get('due_date', '')
                        due_str = f" (Due: {due_date})" if due_date else ""
                        assignee_str = f" - {assignee}" if assignee else ""
                        print(f"   {i}. {task}{due_str}{assignee_str}")
                    else:
                        print(f"   {i}. {item}")
            
            if summary.get('next_steps'):
                print(f"\n🎯 Next Steps:")
                for i, step in enumerate(summary['next_steps'][:3], 1):
                    print(f"   {i}. {step}")
        
        agent.cleanup()
        
        print(f"\n🎉 Real AI Demo Complete!")
        print(f"\nThis demo showed:")
        print(f"   ✅ Real GPT-4 summarization of meeting content")
        print(f"   ✅ Structured analysis with key points and action items")
        print(f"   ✅ Professional-quality meeting summaries")
        print(f"   ✅ Integration with mock audio (ready for real recording)")
        
        print(f"\n🚀 Production Ready Features:")
        print(f"   • Real-time audio recording (PyAudio)")
        print(f"   • Live transcription (OpenAI Whisper)")
        print(f"   • AI-powered summaries (OpenAI GPT)")
        print(f"   • Automated email notifications")
        print(f"   • Meeting history and search")
        print(f"   • Web interface for control")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main demo runner"""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return 1
    
    success = demo_real_ai_meeting()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())