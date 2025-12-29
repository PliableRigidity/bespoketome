"""
Flask web server for Jarvis
Provides a web UI while sharing the same backend as the terminal interface
"""
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dispatcher import handle_user_text
from context_manager import get_context
import os
import json
from datetime import datetime
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Voice assistant instance
voice_assistant = None

# Saved chats file
SAVED_CHATS_FILE = "saved_chats.json"

def load_saved_chats():
    if os.path.exists(SAVED_CHATS_FILE):
        try:
            with open(SAVED_CHATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_saved_chats(chats):
    with open(SAVED_CHATS_FILE, 'w') as f:
        json.dump(chats, f, indent=2)

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/sphere')
def sphere():
    """Serve the particle sphere visualization interface"""
    return render_template('sphere.html')

@app.route('/sphere/demo')
def sphere_demo():
    """Serve the particle sphere demo (no voice assistant required)"""
    return render_template('sphere_demo.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the web UI"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Handle special commands
        context = get_context()
        
        if user_message.lower() == 'clear context':
            context.clear()
            return jsonify({
                'response': 'Conversation history cleared.',
                'system': True
            })
        
        if user_message.lower() == 'show context':
            summary = context.get_summary()
            return jsonify({
                'response': summary,
                'system': True
            })
        
        # Process normal message
        response = handle_user_text(user_message)
        
        return jsonify({
            'response': response,
            'system': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/context', methods=['GET'])
def get_context_api():
    """Get conversation context"""
    context = get_context()
    return jsonify({
        'history': list(context.history)
    })

@app.route('/api/context', methods=['DELETE'])
def clear_context_api():
    """Clear conversation context"""
    context = get_context()
    context.clear()
    return jsonify({'message': 'Context cleared'})

# --- Saved Chats Endpoints ---

@app.route('/api/saved', methods=['GET'])
def get_saved_chats():
    return jsonify({"saved": load_saved_chats()})

@app.route('/api/saved', methods=['POST'])
def save_chat():
    data = request.json
    content = data.get('content')
    # Use first 30 chars as title if not provided
    title = data.get('title', content[:30] + '...' if content else 'Saved Chat')
    
    if not content:
        return jsonify({"error": "No content"}), 400
        
    chats = load_saved_chats()
    new_chat = {
        "id": int(datetime.now().timestamp()), # Simple unique ID
        "title": title,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    chats.append(new_chat)
    save_saved_chats(chats)
    
    return jsonify({"message": "Saved", "chat": new_chat})

@app.route('/api/saved/<int:chat_id>', methods=['DELETE'])
def delete_saved_chat(chat_id):
    chats = load_saved_chats()
    chats = [c for c in chats if c['id'] != chat_id]
    save_saved_chats(chats)
    return jsonify({"message": "Deleted"})

# --- Voice Assistant Endpoints ---

@app.route('/api/voice/start', methods=['POST'])
def start_voice_assistant():
    """Start the voice assistant"""
    global voice_assistant
    
    try:
        if voice_assistant is None:
            from voice_module import VoiceAssistant
            
            def voice_callback(command_text):
                """Handle voice commands"""
                response = handle_user_text(command_text)
                # Emit to frontend
                socketio.emit('voice_interaction', {
                    'command': command_text,
                    'response': response
                })
                return response
            
            def status_callback(status):
                """Handle status updates"""
                socketio.emit('voice_status', {'status': status})
            
            def audio_level_callback(level):
                """Handle audio level updates for visualization"""
                socketio.emit('audio_level', {'level': level})
            
            voice_assistant = VoiceAssistant(callback=voice_callback)
            voice_assistant.set_status_callback(status_callback)
            voice_assistant.set_audio_level_callback(audio_level_callback)
            
            # Set Piper model if configured
            data = request.get_json() or {}
            piper_model = data.get('piper_model') or config.PIPER_MODEL_PATH
            piper_config = data.get('piper_config') or config.PIPER_CONFIG_PATH
            
            if piper_model:
                voice_assistant.set_piper_model(piper_model, piper_config)
        
        voice_assistant.start()
        return jsonify({"status": "started"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice/stop', methods=['POST'])
def stop_voice_assistant():
    """Stop the voice assistant"""
    global voice_assistant
    
    try:
        if voice_assistant:
            voice_assistant.stop()
        return jsonify({"status": "stopped"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice/status', methods=['GET'])
def get_voice_status():
    """Get voice assistant status"""
    global voice_assistant
    
    if voice_assistant:
        return jsonify({
            "running": voice_assistant.is_running,
            "status": voice_assistant.status
        })
    else:
        return jsonify({
            "running": False,
            "status": "not_initialized"
        })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("="*60)
    print("JARVIS WEB INTERFACE")
    print("="*60)
    print("Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
