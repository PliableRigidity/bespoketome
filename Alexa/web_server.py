"""
Flask web server for Vector
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
import database as db
import requests
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vector-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Voice assistant instance
voice_assistant = None
# Robot Sim State
SIMBOT_STATE = {"x": 0, "y": 0, "theta": 0, "status": "idle"}
ROBOT_ESTOP = False

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
                'response': {'text': 'Conversation history cleared.', 'images': [], 'sources': []},
                'system': True
            })
        
        if user_message.lower() == 'show context':
            summary = context.get_summary()
            return jsonify({
                'response': {'text': summary, 'images': [], 'sources': []},
                'system': True
            })
        
        # Process normal message
        response = handle_user_text(user_message)
        
        # Ensure response is structured dict
        if isinstance(response, str):
            response = {'text': response, 'images': [], 'sources': []}
        
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

# --- DOCUMENT UPLOADS ---

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'py', 'js', 'json'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle document uploads and save to memory"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Basic text extraction
        content = ""
        ext = filename.rsplit('.', 1)[1].lower()
        
        try:
            if ext in ['txt', 'md', 'py', 'js', 'json']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            elif ext == 'pdf':
                # Attempt pypdf if available, else placeholder
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
                except ImportError:
                    content = "[PDF Analysis pending: pypdf library not found on server]"
            
            if not content:
                content = f"[File uploaded: {filename}]"

            # Save to memories so dispatcher can use it
            memory_id = db.execute_db(
                "INSERT INTO memories (title, content, source, type, tags) VALUES (?, ?, ?, ?, ?)",
                (f"Document: {filename}", content, 'upload', 'document', f'file-{ext}')
            )
            
            # Save to documents table
            db.execute_db(
                "INSERT INTO documents (filename, file_type, file_path, memory_id) VALUES (?, ?, ?, ?)",
                (filename, ext, file_path, memory_id)
            )
            
            return jsonify({
                'message': 'Intelligence uplink successful',
                'filename': filename,
                'memory_id': memory_id
            })
            
        except Exception as e:
            return jsonify({'error': f'Processing error: {str(e)}'}), 500
            
    return jsonify({'error': 'Protocol violation: File type restricted'}), 400

# --- TASKS ENDPOINTS ---

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = db.query_db("SELECT * FROM tasks ORDER BY created_at DESC")
        return jsonify(list(map(dict, tasks)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        title = data.get('title')
        if not title:
            return jsonify({"error": "Title required"}), 400
        
        db.execute_db(
            "INSERT INTO tasks (title, description, priority, due_date, tags) VALUES (?, ?, ?, ?, ?)",
            (title, data.get('description', ''), data.get('priority', 'medium'), data.get('due_date', ''), data.get('tags', ''))
        )
        return jsonify({"message": "Task created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:id>', methods=['PATCH'])
def update_task(id):
    try:
        data = request.json
        fields = []
        values = []
        for k in ['title', 'description', 'priority', 'due_date', 'status', 'tags']:
            if k in data:
                fields.append(f"{k} = ?")
                values.append(data[k])
        
        if not fields:
            return jsonify({"message": "No changes"}), 200
            
        values.append(id)
        db.execute_db(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", values)
        return jsonify({"message": "Task updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    try:
        db.execute_db("DELETE FROM tasks WHERE id = ?", (id,))
        return jsonify({"message": "Task deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- MEMORY ENDPOINTS ---

@app.route('/api/memory', methods=['GET'])
def get_memories():
    try:
        query = request.args.get('query')
        if query:
            memories = db.query_db(
                "SELECT * FROM memories WHERE content LIKE ? OR title LIKE ? OR tags LIKE ? ORDER BY created_at DESC", 
                (f"%{query}%", f"%{query}%", f"%{query}%")
            )
        else:
            memories = db.query_db("SELECT * FROM memories ORDER BY created_at DESC")
        return jsonify(list(map(dict, memories)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory', methods=['POST'])
def create_memory():
    try:
        data = request.json
        content = data.get('content')
        if not content:
            return jsonify({"error": "Content required"}), 400
            
        db.execute_db(
            "INSERT INTO memories (title, content, source, type, tags) VALUES (?, ?, ?, ?, ?)",
            (data.get('title', ''), content, data.get('source', 'user'), data.get('type', 'pinned'), data.get('tags', ''))
        )
        return jsonify({"message": "Memory saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/<int:id>', methods=['PATCH'])
def update_memory(id):
    try:
        data = request.json
        fields = []
        values = []
        for k in ['title', 'content', 'tags', 'type']:
            if k in data:
                fields.append(f"{k} = ?")
                values.append(data[k])
                
        if not fields:
            return jsonify({"message": "No changes"}), 200
            
        values.append(id)
        db.execute_db(f"UPDATE memories SET {', '.join(fields)} WHERE id = ?", values)
        return jsonify({"message": "Memory updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/<int:id>', methods=['DELETE'])
def delete_memory(id):
    try:
        db.execute_db("DELETE FROM memories WHERE id = ?", (id,))
        return jsonify({"message": "Memory deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RETRIEVAL ENDPOINTS ---

@app.route('/api/retrieval/logs', methods=['GET'])
def get_retrieval_logs():
    try:
        logs = db.query_db("SELECT * FROM retrieval_logs ORDER BY timestamp DESC LIMIT 50")
        return jsonify(list(map(dict, logs)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/retrieval/settings', methods=['GET'])
def get_retrieval_settings():
    try:
        settings = db.query_db("SELECT * FROM retrieval_settings WHERE id = 1", one=True)
        return jsonify(dict(settings))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/retrieval/settings', methods=['POST'])
def update_retrieval_settings():
    try:
        data = request.json
        fields = []
        values = []
        for k in ['web_enabled', 'images_enabled', 'safe_search', 'max_web_results', 'max_image_results']:
            if k in data:
                fields.append(f"{k} = ?")
                values.append(data[k])
        
        if fields:
            values.append(1) # ID = 1
            db.execute_db(f"UPDATE retrieval_settings SET {', '.join(fields)} WHERE id = ?", values)
        
        return jsonify({"message": "Settings updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- SYSTEMS ENDPOINTS ---

@app.route('/api/systems/status', methods=['GET'])
def get_systems_status():
    status = {
        "uptime": "Unknown", # Could track start time
        "llm": {"status": "unknown", "model": config.OLLAMA_MODEL},
        "web": {"status": "unknown"},
        "images": {"status": "unknown"},
        "errors": []
    }
    
    # Check LLM
    try:
        r = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            status["llm"]["status"] = "online"
        else:
            status["llm"]["status"] = "error"
    except:
        status["llm"]["status"] = "offline"

    # Check Web (DuckDuckGo reachability)
    try:
        r = requests.get("https://duckduckgo.com", timeout=2)
        status["web"]["status"] = "online" if r.status_code == 200 else "error"
        status["images"]["status"] = "online" if r.status_code == 200 else "error"
    except:
        status["web"]["status"] = "offline"
        status["images"]["status"] = "offline"
        
    return jsonify(status)

# --- ROBOTS ENDPOINTS ---

@app.route('/api/robots', methods=['GET'])
def get_robots():
    try:
        robots = db.query_db("SELECT * FROM robots")
        # Add live sim state to SimBot
        robots_list = []
        for r in robots:
            rd = dict(r)
            if rd['name'] == 'SimBot-01':
                rd['state'] = SIMBOT_STATE
            robots_list.append(rd)
        return jsonify(robots_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/robots/<int:id>/command', methods=['POST'])
def send_robot_command(id):
    global ROBOT_ESTOP, SIMBOT_STATE
    
    if ROBOT_ESTOP:
        return jsonify({"error": "E-STOP ACTIVE. Command rejected."}), 403
        
    data = request.json
    command = data.get('command')
    args = data.get('args', []) # List of args
    
    # Check if robot exists
    robot = db.query_db("SELECT * FROM robots WHERE id = ?", (id,), one=True)
    if not robot:
        return jsonify({"error": "Robot not found"}), 404
        
    # Log command
    db.execute_db(
        "INSERT INTO robot_commands (robot_id, command, args, status) VALUES (?, ?, ?, ?)",
        (id, command, json.dumps(args), "processed")
    )
    
    # Execute SimBot Logic
    if robot['name'] == 'SimBot-01':
        if command == 'move':
            # args: [dist] -> move forward x dist
            dist = float(args[0]) if args else 0
            # Simple 2D movement
            import math
            SIMBOT_STATE['x'] += dist * math.cos(math.radians(SIMBOT_STATE['theta']))
            SIMBOT_STATE['y'] += dist * math.sin(math.radians(SIMBOT_STATE['theta']))
            SIMBOT_STATE['status'] = 'moving'
        elif command == 'rotate':
            # args: [deg]
            deg = float(args[0]) if args else 0
            SIMBOT_STATE['theta'] = (SIMBOT_STATE['theta'] + deg) % 360
        elif command == 'stop':
            SIMBOT_STATE['status'] = 'idle'
            
        return jsonify({"message": "Command executed", "state": SIMBOT_STATE})
        
    return jsonify({"message": "Command sent (simulated)"})

@app.route('/api/robots/estop', methods=['POST'])
def robot_estop():
    global ROBOT_ESTOP
    data = request.json
    ROBOT_ESTOP = data.get('active', True)
    return jsonify({"message": f"E-STOP {'ACTIVATED' if ROBOT_ESTOP else 'DEACTIVATED'}"})


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
    print("VECTOR WEB INTERFACE")
    print("="*60)
    print("Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
