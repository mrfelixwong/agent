"""
Flask web application for Meeting Agent
Provides a web interface for controlling meetings and viewing history
"""

import json
from datetime import datetime, date
from typing import Dict, Any, Optional

try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
    from flask_socketio import SocketIO, emit
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app(config: Optional[Dict[str, Any]] = None, meeting_agent=None) -> Flask:
    """Create and configure Flask application"""
    
    if not HAS_FLASK:
        raise ImportError("Flask is not installed. Please install with: pip install flask flask-socketio")
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.get('web.secret_key', 'meeting-agent-secret-key') if config else 'default-secret'
    
    # Initialize SocketIO for real-time updates
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Store reference to meeting agent
    app.meeting_agent = meeting_agent
    
    @app.route('/')
    def index():
        """Main dashboard"""
        try:
            if not app.meeting_agent:
                return render_template('error.html', error="Meeting Agent not initialized")
            
            # Get system status
            status = app.meeting_agent.get_system_status()
            
            # Get current meeting status
            meeting_status = app.meeting_agent.get_meeting_status()
            
            # Get recent meetings
            recent_meetings = app.meeting_agent.get_meeting_history(days_back=7)
            
            return render_template('index.html', 
                                 system_status=status,
                                 meeting_status=meeting_status,
                                 recent_meetings=recent_meetings[:10])  # Show last 10
                                 
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/api/status')
    def api_status():
        """Get system and meeting status via API"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            system_status = app.meeting_agent.get_system_status()
            meeting_status = app.meeting_agent.get_meeting_status()
            
            return jsonify({
                'system': system_status,
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
            meeting_name = data.get('name', '').strip()
            participants = data.get('participants', [])
            
            if not meeting_name:
                return jsonify({'error': 'Meeting name is required'}), 400
            
            # Start the meeting
            meeting_info = app.meeting_agent.start_meeting(meeting_name, participants)
            
            logger.info(f"Meeting started via API: {meeting_name}")
            return jsonify({
                'success': True,
                'meeting': meeting_info
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Start meeting API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stop_meeting', methods=['POST'])
    def api_stop_meeting():
        """Stop the current meeting"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            # Stop the meeting
            completed_meeting = app.meeting_agent.stop_meeting()
            
            logger.info(f"Meeting stopped via API: {completed_meeting.get('name', 'Unknown')}")
            return jsonify({
                'success': True,
                'meeting': completed_meeting
            })
            
        except ValueError as e:
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
    
    @app.route('/api/search')
    def api_search():
        """Search meetings"""
        try:
            if not app.meeting_agent:
                return jsonify({'error': 'Meeting Agent not initialized'}), 500
            
            query = request.args.get('q', '').strip()
            limit = request.args.get('limit', 10, type=int)
            
            if not query:
                return jsonify({'error': 'Search query is required'}), 400
            
            results = app.meeting_agent.search_meetings(query, limit)
            
            return jsonify({
                'results': results,
                'query': query,
                'total': len(results)
            })
            
        except Exception as e:
            logger.error(f"Search API error: {e}")
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
    
    @app.route('/settings')
    def settings_page():
        """Settings page"""
        try:
            if not app.meeting_agent:
                return render_template('error.html', error="Meeting Agent not initialized")
            
            system_status = app.meeting_agent.get_system_status()
            
            return render_template('settings.html', system_status=system_status)
            
        except Exception as e:
            logger.error(f"Settings page error: {e}")
            return render_template('error.html', error=str(e))
    
    # WebSocket events for real-time updates
    @socketio.on('connect')
    def handle_connect():
        """Handle WebSocket connection"""
        logger.info("WebSocket client connected")
        emit('status', {'message': 'Connected to Meeting Agent'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnection"""
        logger.info("WebSocket client disconnected")
    
    @socketio.on('get_status')
    def handle_get_status():
        """Handle status request via WebSocket"""
        try:
            if app.meeting_agent:
                meeting_status = app.meeting_agent.get_meeting_status()
                emit('meeting_status', meeting_status)
            else:
                emit('error', {'message': 'Meeting Agent not initialized'})
        except Exception as e:
            emit('error', {'message': str(e)})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error="Internal server error"), 500
    
    # Store socketio instance on app for external access
    app.socketio = socketio
    
    return app


def create_simple_app(meeting_agent) -> Flask:
    """Create a simple Flask app without complex dependencies"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'simple-meeting-agent-key'
    app.meeting_agent = meeting_agent
    
    @app.route('/')
    def simple_index():
        """Simple HTML dashboard"""
        try:
            status = app.meeting_agent.get_meeting_status()
            system_status = app.meeting_agent.get_system_status()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Meeting Agent Dashboard</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .status {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                    .button {{ background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }}
                    .button:hover {{ background: #005a8b; }}
                    .error {{ color: red; }}
                    .success {{ color: green; }}
                    input[type="text"] {{ padding: 8px; width: 200px; margin: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎙️ Meeting Agent Dashboard</h1>
                    
                    <div class="status">
                        <h3>Current Status</h3>
                        <p><strong>Meeting Status:</strong> {status.get('status', 'Unknown')}</p>
                        <p><strong>System Status:</strong> {system_status.get('status', 'Unknown')}</p>
                        
                        {'<p><strong>Current Meeting:</strong> ' + status.get('meeting', {}).get('name', 'None') + '</p>' if status.get('meeting') else ''}
                        {'<p><strong>Current Transcription Cost:</strong> $' + f"{status.get('cost_info', {}).get('total_cost', 0.0):.4f}" + ' (' + f"{status.get('cost_info', {}).get('total_duration_minutes', 0.0):.1f}" + ' minutes)</p>' if status.get('meeting') else ''}
                    </div>
                    
                    <div class="controls">
                        <h3>Meeting Controls</h3>
                        <form method="post" action="/start_meeting">
                            <input type="text" name="meeting_name" placeholder="Meeting name..." required>
                            <input type="text" name="participants" placeholder="Participants (comma-separated)">
                            <button type="submit" class="button">Start Meeting</button>
                        </form>
                        
                        <form method="post" action="/stop_meeting" style="display: inline;">
                            <button type="submit" class="button">Stop Meeting</button>
                        </form>
                    </div>
                    
                    <div class="recent">
                        <h3>Recent Meetings</h3>
                        <p><a href="/meetings">View meeting history →</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p>"
    
    @app.route('/start_meeting', methods=['POST'])
    def simple_start_meeting():
        """Simple start meeting endpoint"""
        try:
            meeting_name = request.form.get('meeting_name', '').strip()
            participants_str = request.form.get('participants', '').strip()
            
            participants = [p.strip() for p in participants_str.split(',') if p.strip()] if participants_str else []
            
            if not meeting_name:
                return "<h1>Error</h1><p>Meeting name is required</p><a href='/'>← Back</a>"
            
            meeting_info = app.meeting_agent.start_meeting(meeting_name, participants)
            
            return f"""
            <h1>Meeting Started</h1>
            <p>Meeting "{meeting_name}" started successfully!</p>
            <p>Meeting ID: {meeting_info['id']}</p>
            <a href="/">← Back to dashboard</a>
            """
            
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p><a href='/'>← Back</a>"
    
    @app.route('/stop_meeting', methods=['POST'])
    def simple_stop_meeting():
        """Simple stop meeting endpoint"""
        try:
            meeting_info = app.meeting_agent.stop_meeting()
            
            cost_info = meeting_info.get('cost_info', {})
            return f"""
            <h1>Meeting Stopped</h1>
            <p>Meeting "{meeting_info.get('name', 'Unknown')}" completed successfully!</p>
            <p>Duration: {meeting_info.get('duration_minutes', 0)} minutes</p>
            <p>Transcription Cost: ${cost_info.get('total_cost', 0.0):.4f}</p>
            <a href="/">← Back to dashboard</a>
            """
            
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p><a href='/'>← Back</a>"
    
    @app.route('/meetings')
    def simple_meetings():
        """Simple meetings list"""
        try:
            meetings = app.meeting_agent.get_meeting_history(days_back=7)
            
            # Calculate total cost
            total_cost = sum(meeting.get('transcription_cost', 0.0) for meeting in meetings)
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Meeting History</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .summary { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📋 Meeting History</h1>
                    <p><a href="/">← Back to dashboard</a></p>
                    
                    <div class="summary">
                        <h3>Summary (Last 7 Days)</h3>
                        <p><strong>Total Meetings:</strong> """ + str(len(meetings)) + """</p>
                        <p><strong>Total Transcription Cost:</strong> $""" + f"{total_cost:.4f}" + """</p>
                    </div>
                    
                    <table>
                        <tr>
                            <th>Date</th>
                            <th>Name</th>
                            <th>Duration</th>
                            <th>Transcription Cost</th>
                            <th>Status</th>
                        </tr>
            """
            
            for meeting in meetings[:20]:  # Show last 20
                date_str = meeting.get('date', 'Unknown')
                name = meeting.get('name', 'Unknown')
                duration = meeting.get('duration_minutes', 0)
                cost = meeting.get('transcription_cost', 0.0)
                status = meeting.get('status', 'Unknown')
                
                html += f"""
                        <tr>
                            <td>{date_str}</td>
                            <td>{name}</td>
                            <td>{duration} min</td>
                            <td>${cost:.4f}</td>
                            <td>{status}</td>
                        </tr>
                """
            
            html += """
                    </table>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p><a href='/'>← Back</a>"
    
    return app