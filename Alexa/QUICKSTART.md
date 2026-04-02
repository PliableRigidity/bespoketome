# 🚀 VECTOR Modules - Quick Start Guide

## ✅ Everything is Already Implemented!

All 5 modules are **fully functional** and ready to use. This guide will help you explore the features.

---

## 🎯 Quick Start (3 Steps)

### 1. Start the Server
```bash
.\run_web.bat
```

### 2. Open Browser
Navigate to: **http://localhost:5000**

### 3. Explore Modules
Click the sidebar icons to switch between modules!

---

## 📚 Module Guide

### 💬 CHAT (Existing - Unchanged)
**What it does:** Your AI assistant with web search and image capabilities

**Try this:**
1. Ask: "What is quantum computing?"
2. Notice the assistant response with sources
3. Look at the action buttons below the message:
   - **🧠 Save** - Save this response to Memory
   - **✓ Task** - Create a task from this response
   - **🔍 Retrieval** - View the search logs

---

### ✓ TASKS Module
**What it does:** Track and manage your tasks

**Try this:**
1. Click the **Tasks** icon in the sidebar
2. Click **"+ New Task"** button
3. Fill in:
   - Title: "Learn about quantum computing"
   - Description: "Research quantum computing basics"
   - Priority: High
4. Click **Create**
5. See your task appear with a red "HIGH" badge
6. Click the **✓** button to mark it complete
7. Watch it get a strikethrough
8. Try the filters: **All** / **Active** / **Completed**

**Quick Action:**
- Go back to Chat
- Ask the assistant something
- Click **✓ Task** on the response
- See the modal pre-filled with the response!

---

### 🧠 MEMORY Module
**What it does:** Save and search long-term memories

**Try this:**
1. Click the **Memory** icon in the sidebar
2. Click **"+ Add Memory"** button
3. Fill in:
   - Title: "Quantum Computing Notes"
   - Content: "Quantum computers use qubits instead of bits..."
   - Tags: "physics, computing, research"
4. Click **Save**
5. See your memory card appear
6. Try searching: Type "quantum" in the search box
7. Press Enter - see filtered results

**Quick Action:**
- Go back to Chat
- Ask the assistant something interesting
- Click **🧠 Save** on the response
- See the modal pre-filled!
- Add tags and save

---

### 🔍 RETRIEVAL Module
**What it does:** View search history and control retrieval settings

**Try this:**
1. Click the **Retrieval** icon in the sidebar
2. See recent searches in the logs
3. Each log shows:
   - The query used
   - Number of sources found
   - Number of images found
   - Timestamp
4. Try the settings:
   - Toggle **Web Search** off
   - Toggle **Image Search** off
   - Change **Safe Search** level
5. Go back to Chat and ask something
6. Return to Retrieval - see the new log entry!

**Settings:**
- **Web Search ON/OFF** - Enable/disable web searches
- **Image Search ON/OFF** - Enable/disable image searches
- **Safe Search** - Strict / Moderate / Off

---

### ⚙️ SYSTEMS Module
**What it does:** Monitor system health and status

**Try this:**
1. Click the **Systems** icon in the sidebar
2. See status cards:
   - **🧠 LLM Engine** - Shows if Ollama is running
   - **🌐 Web Search** - Shows if DuckDuckGo is reachable
   - **🖼 Image Search** - Shows if image search is working
3. Each card shows:
   - Green 🟢 = Online
   - Red 🔴 = Offline
   - Yellow 🟡 = Error
4. Click **Refresh Status** to update

**Troubleshooting:**
- If LLM shows offline: Make sure Ollama is running
- If Web/Images show offline: Check internet connection

---

### 🤖 ROBOTS Module
**What it does:** Control simulated robots (SimBot-01 included!)

**Try this:**
1. Click the **Robots** icon in the sidebar
2. See **SimBot-01** in the robot list
3. Click on SimBot-01 to select it
4. See the control panel appear with buttons:
   - **Move Fwd** - Move forward 10 units
   - **Turn Right** - Rotate 90 degrees
   - **STOP** - Stop movement
5. Click **Move Fwd** a few times
6. Watch the visualizer update!
   - Blue dot = robot position
   - White arrow = facing direction
   - X, Y, θ coordinates shown
7. Try **Turn Right** - see the arrow rotate
8. Try the **E-STOP** button:
   - Click it - turns red with glow
   - Try to move - command rejected!
   - Click again to reset

**E-STOP Safety:**
- When E-STOP is active (red), ALL robot commands are blocked
- This is a safety feature for real robot integration later
- Always reset E-STOP before sending commands

---

## 🎨 UI Features

### Action Buttons on Messages
Every assistant message has action buttons:
- **🧠 Save** - Opens Memory modal with response pre-filled
- **✓ Task** - Opens Task modal with response as title
- **🔍 Retrieval** - Jumps to Retrieval module (if sources/images present)

### Filters & Search
- **Tasks:** Filter by All/Active/Completed
- **Memory:** Search by keyword (searches title, content, tags)
- **Retrieval:** View chronological logs

### Visual Feedback
- **Priority Badges:** High (red), Medium (orange), Low (green)
- **Status Indicators:** Online (green), Offline (red), Error (yellow)
- **Completed Tasks:** Strikethrough text, reduced opacity
- **Empty States:** Helpful messages when no data exists

---

## 🧪 Testing

### Run Automated Tests
```bash
python test_modules.py
```

This will test:
- ✅ Creating, listing, updating, deleting tasks
- ✅ Creating, searching, deleting memories
- ✅ Getting and updating retrieval settings
- ✅ Getting system status
- ✅ Listing robots and sending commands
- ✅ E-STOP functionality

### Manual Testing Workflow
1. **Chat → Task:**
   - Ask assistant a question
   - Click ✓ Task button
   - Create task
   - Go to Tasks module
   - Mark it complete

2. **Chat → Memory:**
   - Ask assistant something interesting
   - Click 🧠 Save button
   - Add tags
   - Save
   - Go to Memory module
   - Search for it

3. **Retrieval Logging:**
   - Ask assistant to search for something
   - Go to Retrieval module
   - See the log entry
   - Toggle settings
   - Ask again
   - See new log

4. **Robot Control:**
   - Go to Robots module
   - Select SimBot-01
   - Move forward 3 times
   - Turn right 2 times
   - See position change in visualizer
   - Activate E-STOP
   - Try to move (should fail)
   - Deactivate E-STOP

---

## 📊 Database

### Location
`vector_state.db` in the project root

### View Database (Optional)
```bash
# Install DB Browser for SQLite (optional)
# Or use command line:
sqlite3 vector_state.db
.tables
SELECT * FROM tasks;
SELECT * FROM memories;
.quit
```

### Reset Database
```bash
# Delete the database file
del vector_state.db

# Restart server - it will auto-recreate
.\run_web.bat
```

---

## 🎯 Common Workflows

### Workflow 1: Research Assistant
1. Ask assistant about a topic
2. Click **🧠 Save** to save the response
3. Click **✓ Task** to create a follow-up task
4. Go to **Retrieval** to see what sources were used
5. Go to **Memory** to review saved notes
6. Go to **Tasks** to track your research tasks

### Workflow 2: System Monitoring
1. Go to **Systems** module
2. Check all services are online
3. If something is offline, troubleshoot:
   - LLM offline? Start Ollama
   - Web offline? Check internet
4. Click **Refresh** to verify

### Workflow 3: Robot Experimentation
1. Go to **Robots** module
2. Select SimBot-01
3. Create a path:
   - Move forward
   - Turn right
   - Move forward
   - Turn right
   - (Creates a square!)
4. Watch the visualizer trace the path

---

## 🆘 Troubleshooting

### Module Not Loading
- **Check browser console** for JavaScript errors
- **Refresh page** (Ctrl+F5)
- **Check server logs** in terminal

### Database Errors
- **Delete vector_state.db** and restart
- **Check file permissions**

### Robot Not Moving
- **Check E-STOP** is not active (should not be red)
- **Refresh page** to reset state

### No Retrieval Logs
- **Ask a question first** to generate logs
- **Check dispatcher.py** is logging correctly

---

## 🎉 You're All Set!

All 5 modules are fully functional and ready to use. Explore, experiment, and enjoy your VECTOR AI assistant!

**Need help?** Check:
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `ARCHITECTURE.md` - System architecture
- `MODULE_STATUS.md` - Complete status report
- `README.md` - General information

**Happy exploring! 🚀**
