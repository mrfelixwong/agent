#!/usr/bin/env python3
"""
Meeting Agent - Main Entry Point
Intelligent meeting recording and summarization system
"""

import os
import sys
import signal
import threading
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import MeetingAgent
from src.utils.logger import setup_logger
from src.utils.config import load_config

logger = setup_logger(__name__)

def signal_handler(signum, frame):
    """Handle graceful shutdown"""
    logger.info("Received shutdown signal, stopping Meeting Agent...")
    if hasattr(signal_handler, 'agent'):
        signal_handler.agent.stop()
    sys.exit(0)

def main():
    """Main entry point"""
    try:
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Load configuration
        config = load_config()
        
        # Create and start the meeting agent
        logger.info("Starting Meeting Agent...")
        agent = MeetingAgent(config)
        signal_handler.agent = agent
        
        # Start the agent
        agent.start()
        
        logger.info("Meeting Agent started successfully!")
        logger.info(f"Web interface available at: http://{config['web']['host']}:{config['web']['port']}")
        
        # Keep main thread alive
        try:
            while True:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            pass
            
    except Exception as e:
        logger.error(f"Failed to start Meeting Agent: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Meeting Agent stopped.")

if __name__ == "__main__":
    main()