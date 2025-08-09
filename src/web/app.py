"""Flask web application for Meeting Agent - Web interface for meetings"""

import json
from datetime import datetime, date
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify

from ..utils.logger import setup_logger
from ..utils.config import get_config_value

logger = setup_logger(__name__)

def create_app(config: Optional[Dict[str, Any]] = None, meeting_agent=None) -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = get_config_value(config, 'web.secret_key', 'meeting-agent-secret-key') if config else 'default-secret'
    
    app.meeting_agent = meeting_agent
    
    @app.route('/')
    def index():
        try:
            if not app.meeting_agent:
                return render_template('error.html', error="Meeting Agent not initialized")
            meeting_status = app.meeting_agent.get_meeting_status()
            recent_meetings = app.meeting_agent.get_meeting_history(days_back=7)
            
            return render_template('index.html', 
                                 meeting_status=meeting_status,
                                 recent_meetings=recent_meetings[:10])
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/api/status')
    def api_status():
        """Get meeting status"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            meeting_status = app.meeting_agent.get_meeting_status()
            
            return jsonify({
                'meeting': meeting_status
            })
            
        except Exception as e:
            logger.error(f"Status API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/start_meeting', methods=['POST'])
    def api_start_meeting():
        """Start a new meeting"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data received'}), 400
            
            meeting_name = data.get('name', '').strip()
            if not meeting_name:
                return jsonify({'error': 'Meeting name is required'}), 400
            
            # Start the meeting
            meeting_info = app.meeting_agent.start_meeting(meeting_name)
            
            return jsonify({
                'success': True,
                'meeting': meeting_info
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stop_meeting', methods=['POST'])
    def api_stop_meeting():
        """Stop the current meeting"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            # Stop the meeting
            completed_meeting = app.meeting_agent.stop_meeting()
            
            return jsonify({
                'success': True,
                'meeting': completed_meeting
            })
            
        except ValueError as e:
            logger.error(f"ValueError in stop_meeting: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Stop meeting API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/meetings')
    def api_meetings():
        """Get meeting history"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            days_back = request.args.get('days', 30, type=int)
            meetings = app.meeting_agent.get_meeting_history(days_back)
            
            return jsonify({
                'meetings': meetings,
                'total': len(meetings)
            })
            
        except Exception as e:
            logger.error(f"Meetings API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/meetings/<int:meeting_id>')
    def api_meeting_details(meeting_id: int):
        """Get detailed meeting information"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            meeting = app.meeting_agent.get_meeting_details(meeting_id)
            
            if not meeting:
                return jsonify({'error': 'Meeting not found'}), 404
            
            return jsonify(meeting)
            
        except Exception as e:
            logger.error(f"Meeting details API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/daily_summary')
    def api_daily_summary():
        """Generate and get daily summary"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            date_str = request.args.get('date')
            target_date = None
            
            if date_str:
                try:
                    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
            summary = app.meeting_agent.generate_daily_summary(target_date)
            
            return jsonify(summary)
            
        except Exception as e:
            logger.error(f"Daily summary API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/send_daily_email', methods=['POST'])
    def api_send_daily_email():
        """Send daily summary email"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            data = request.get_json() or {}
            date_str = data.get('date')
            target_date = None
            
            if date_str:
                try:
                    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
            success = app.meeting_agent.send_daily_summary_email(target_date)
            
            return jsonify({
                'success': success,
                'message': 'Daily summary email sent' if success else 'Failed to send daily summary email'
            })
            
        except Exception as e:
            logger.error(f"Send daily email API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/meetings')
    def meetings_page():
        """Meeting history page"""
        try:
            if not app.meeting_agent:
                    return render_template('error.html', error="Meeting Agent not initialized")
            
            meetings = app.meeting_agent.get_meeting_history(days_back=30)
            
            return render_template('meetings.html', meetings=meetings)
            
        except Exception as e:
            logger.error(f"Meetings page error: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/meetings/<int:meeting_id>')
    def meeting_details_page(meeting_id: int):
        """Meeting details page"""
        try:
            if not app.meeting_agent:
                return render_template('error.html', error="Meeting Agent not initialized")
            
            meeting = app.meeting_agent.get_meeting_details(meeting_id)
            
            if not meeting:
                    return render_template('error.html', error="Meeting not found")
            
            return render_template('meeting_details.html', meeting=meeting)
            
        except Exception as e:
            logger.error(f"Meeting details page error: {e}")
            return render_template('error.html', error=str(e))
    
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error="Internal server error"), 500
    
    return app
