import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
from groq import Groq

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key == "your_groq_api_key_here":
    print("[!] Error: GROQ_API_KEY not found in .env file.")
    print("Please update your .env file with a valid Groq API key.")
    print("Get your API key from: https://console.groq.com/keys")
    sys.exit(1)

client = Groq(api_key=api_key)

# System prompt - Strict AV Focus
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "🚗 You are AVExpert - The World's Leading Autonomous Vehicle AI Assistant\n\n"

        "=========================\n"
        "🎯 CORE IDENTITY & BOUNDARIES\n"
        "=========================\n"
        "You are EXCLUSIVELY specialized in Autonomous Vehicles (AV) and Self-Driving Cars.\n"
        "You ONLY discuss topics related to:\n"
        "- Autonomous Vehicle Technology\n"
        "- Self-Driving Car Systems\n"
        "- AV Hardware & Software\n"
        "- Transportation Automation\n"
        "- Vehicle AI & Robotics\n\n"

        "🚫 STRICT BOUNDARIES:\n"
        "If asked about ANY topic outside Autonomous Vehicles, respond with:\n"
        "\"🚗 I'm AVExpert, specialized exclusively in Autonomous Vehicle technology. I don't have information about [topic]. Please ask me about self-driving cars, AV sensors, SAE levels, path planning, or any autonomous vehicle technology!\"\n\n"

        "=========================\n"
        "📋 RESPONSE FORMAT (ALWAYS USE)\n"
        "=========================\n"
        "Structure every AV response as:\n\n"

        "## 🎯 Quick Answer\n"
        "[2-3 sentence direct answer]\n\n"

        "## 🔍 Technical Deep Dive\n"
        "### Core Components:\n"
        "- **Component 1**: Explanation\n"
        "- **Component 2**: Explanation\n\n"

        "### How It Works:\n"
        "1. **Step 1**: Process\n"
        "2. **Step 2**: Process\n\n"

        "## 📊 Comparison Table (when applicable)\n"
        "| Feature | Option A | Option B |\n"
        "|---------|----------|----------|\n"
        "| Aspect  | Details  | Details  |\n\n"

        "## 🏢 Real-World Examples\n"
        "- **Tesla**: Implementation details\n"
        "- **Waymo**: Implementation details\n"
        "- **Other Companies**: Details\n\n"

        "## ⚡ Key Takeaways\n"
        "- Point 1\n"
        "- Point 2\n"
        "- Point 3\n\n"

        "=========================\n"
        "🚗 EXPERTISE DOMAINS\n"
        "=========================\n"
        "Your knowledge covers:\n\n"

        "**🎚️ SAE Automation Levels:**\n"
        "- Level 0-5 definitions and differences\n"
        "- Real-world implementations\n\n"

        "**📡 Sensor Technologies:**\n"
        "- LiDAR, Radar, Cameras, Ultrasonic\n"
        "- Sensor fusion techniques\n"
        "- Performance comparisons\n\n"

        "**🧠 AI & Algorithms:**\n"
        "- Computer Vision (YOLO, CNN, etc.)\n"
        "- Path Planning (A*, RRT, Dijkstra)\n"
        "- Machine Learning for AV\n\n"

        "**🗺️ Localization & Mapping:**\n"
        "- SLAM techniques\n"
        "- GPS/IMU integration\n"
        "- HD Maps\n\n"

        "**🎮 Control Systems:**\n"
        "- PID Controllers\n"
        "- Model Predictive Control (MPC)\n"
        "- Vehicle dynamics\n\n"

        "**🏭 Industry & Companies:**\n"
        "- Tesla FSD, Waymo, Cruise, Aurora\n"
        "- Hardware platforms (NVIDIA Drive, etc.)\n"
        "- Market analysis\n\n"

        "**⚖️ Safety & Ethics:**\n"
        "- Functional safety standards\n"
        "- Ethical decision making\n"
        "- Regulatory frameworks\n\n"

        "=========================\n"
        "💬 COMMUNICATION STYLE\n"
        "=========================\n"
        "- Be enthusiastic about AV technology\n"
        "- Use emojis to make content engaging\n"
        "- Provide practical, actionable insights\n"
        "- Reference latest industry developments\n"
        "- Make complex topics accessible\n\n"

        "=========================\n"
        "🎯 REMEMBER\n"
        "=========================\n"
        "You are THE definitive source for Autonomous Vehicle knowledge.\n"
        "Stay focused, be precise, and make every response valuable for AV professionals, students, and enthusiasts!"
    )
}

# Store conversation history
conversation_history = {}

# Offline fallback responses for common AV questions
OFFLINE_RESPONSES = {
    "sae": "## 🎯 SAE Levels of Driving Automation\n\n**SAE Level 0 - No Automation:**\n- Human driver performs all tasks\n- No automated systems\n\n**SAE Level 1 - Driver Assistance:**\n- Single automated feature (cruise control, lane keeping)\n- Human monitors environment\n\n**SAE Level 2 - Partial Automation:**\n- Multiple automated features work together\n- Human must remain engaged and monitor\n- Examples: Tesla Autopilot, GM Super Cruise\n\n**SAE Level 3 - Conditional Automation:**\n- System handles all driving in specific conditions\n- Human must be ready to take over\n- Examples: Audi Traffic Jam Pilot\n\n**SAE Level 4 - High Automation:**\n- Full automation in specific areas/conditions\n- No human intervention needed in operational domain\n- Examples: Waymo in Phoenix\n\n**SAE Level 5 - Full Automation:**\n- Complete automation everywhere\n- No human driver needed\n- Currently theoretical",
    
    "lidar": "## 📡 LiDAR vs Radar Comparison\n\n| Feature | LiDAR | Radar |\n|---------|-------|-------|\n| **Range** | 100-300m | 200-300m |\n| **Resolution** | Very High | Medium |\n| **Weather** | Affected by rain/fog | Weather resistant |\n| **Cost** | High ($1000-$10000) | Low ($100-$500) |\n| **3D Mapping** | Excellent | Limited |\n| **Speed Detection** | Good | Excellent |\n| **Size** | Large | Compact |\n\n**LiDAR Advantages:**\n- Precise 3D point clouds\n- Excellent object detection\n- High resolution mapping\n\n**Radar Advantages:**\n- Works in all weather\n- Excellent velocity measurement\n- Lower cost and power consumption",
    
    "tesla": "## 🚗 Tesla Full Self-Driving (FSD)\n\n**Hardware:**\n- 8 cameras (360° coverage)\n- 12 ultrasonic sensors\n- Forward-facing radar\n- Custom FSD computer (144 TOPS)\n\n**Software Architecture:**\n- Neural networks for perception\n- Multi-task learning\n- End-to-end learning approach\n- Over-the-air updates\n\n**Key Features:**\n- Navigate on Autopilot\n- Auto Lane Change\n- Summon\n- Traffic Light Recognition\n- City Street Driving (Beta)\n\n**Approach:**\n- Vision-first strategy\n- Massive fleet learning\n- Simulation training\n- Real-world data collection",
    
    "waymo": "## 🚙 Waymo Autonomous Driving\n\n**Hardware Stack:**\n- Custom LiDAR sensors\n- High-resolution cameras\n- Radar sensors\n- Powerful onboard computers\n\n**Software Approach:**\n- Detailed HD maps\n- Sensor fusion algorithms\n- Machine learning models\n- Extensive simulation testing\n\n**Operational Design Domain:**\n- Geofenced areas\n- Pre-mapped routes\n- Specific weather conditions\n- Urban and suburban environments\n\n**Key Achievements:**\n- Over 20 million autonomous miles\n- Commercial robotaxi service\n- SAE Level 4 automation\n- Safety-first approach"
}

def get_offline_response(message):
    """Get offline response for common AV questions"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['sae', 'level', 'automation']):
        return OFFLINE_RESPONSES['sae']
    elif any(word in message_lower for word in ['lidar', 'radar', 'sensor']):
        return OFFLINE_RESPONSES['lidar']
    elif 'tesla' in message_lower or 'fsd' in message_lower:
        return OFFLINE_RESPONSES['tesla']
    elif 'waymo' in message_lower:
        return OFFLINE_RESPONSES['waymo']
    else:
        return "🚗 **AV Intelligence - Offline Mode**\n\nI'm currently running in offline mode. I can help with these topics:\n\n• **SAE Levels** - Ask about 'SAE levels' or 'automation levels'\n• **Sensors** - Ask about 'LiDAR vs Radar' or 'sensors'\n• **Tesla FSD** - Ask about 'Tesla' or 'FSD'\n• **Waymo** - Ask about 'Waymo'\n\nTry asking: *'Explain SAE levels'* or *'Compare LiDAR vs Radar'*"

def get_response(message, session_id):
    """Get response from Groq API with improved error handling and offline fallback"""
    try:
        # Initialize conversation history for new sessions
        if session_id not in conversation_history:
            conversation_history[session_id] = [SYSTEM_PROMPT]
        
        # Add user message
        conversation_history[session_id].append({"role": "user", "content": message})
        
        # Get AI response with better error handling
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Updated to current working model
            messages=conversation_history[session_id],
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        response = completion.choices[0].message.content
        
        # Add AI response to history
        conversation_history[session_id].append({"role": "assistant", "content": response})
        
        return response
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"[ERROR] API failed, trying offline mode: {error_msg}")
        
        # Try offline response first
        offline_response = get_offline_response(message)
        if "Offline Mode" not in offline_response:
            return offline_response
        
        # Return detailed error messages
        if "rate limit" in error_msg or "429" in error_msg:
            return "⚠️ **Rate Limit Reached**\n\nThe API rate limit has been exceeded. Please wait a moment and try again.\n\n*Tip: Try asking shorter questions or wait 1-2 minutes between requests.*"
        
        elif "api key" in error_msg or "401" in error_msg or "unauthorized" in error_msg:
            return "🔑 **API Key Issue**\n\nThere's an issue with the API key configuration.\n\n**Solutions:**\n- Check if your Groq API key is valid\n- Verify the key in your .env file\n- Get a new key from: https://console.groq.com/keys\n\n**Offline Mode Available:**\nTry asking about: SAE levels, LiDAR vs Radar, Tesla FSD, or Waymo"
        
        elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg or "failed to fetch" in error_msg:
            return f"🌐 **Connection Issue - Offline Mode Active**\n\nUnable to connect to the Groq servers, but I can still help with common AV topics!\n\n**Available offline topics:**\n• SAE Levels of automation\n• LiDAR vs Radar comparison\n• Tesla FSD overview\n• Waymo technology\n\n**Try asking:** *'Explain SAE levels'* or *'Compare LiDAR vs Radar'*"
        
        else:
            # Return clean offline response for any other error
            offline_response = get_offline_response(message)
            if "Offline Mode" not in offline_response:
                return offline_response
            else:
                return f"❌ **System Error - Offline Mode Available**\n\n{offline_response}"

@app.route('/')
def index():
    """Serve the premium ChatGPT-style interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"[ERROR] Template error: {str(e)}")
        return f"""
        <html>
        <head><title>AVExpert - Template Error</title></head>
        <body style="font-family: Arial; padding: 20px; background: #212121; color: white;">
            <h1>🚗 AVExpert - Autonomous Vehicle AI</h1>
            <p>Template loading error: {str(e)}</p>
            <p><a href="/standalone" style="color: #10A37F;">Try Standalone Version</a></p>
            <p><a href="/simple" style="color: #10A37F;">Try Simple Version</a></p>
        </body>
        </html>
        """

@app.route('/simple')
def simple():
    """Simple working version"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AVExpert - Simple Version</title>
        <style>
            body { font-family: Arial; background: #212121; color: white; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
            .user { background: #10A37F; text-align: right; }
            .bot { background: #444654; }
            input { width: 70%; padding: 10px; background: #40414F; border: none; color: white; }
            button { padding: 10px 20px; background: #10A37F; border: none; color: white; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 AVExpert - Autonomous Vehicle AI</h1>
            <div id="messages"></div>
            <div>
                <input type="text" id="messageInput" placeholder="Ask about autonomous vehicles...">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML += `<div class="message user">${message}</div>`;
                input.value = '';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message, session_id: 'simple' })
                    });
                    const data = await response.json();
                    messagesDiv.innerHTML += `<div class="message bot">${data.response || data.error}</div>`;
                } catch (error) {
                    messagesDiv.innerHTML += `<div class="message bot">Error: ${error.message}</div>`;
                }
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """

@app.route('/standalone')
def standalone():
    """Serve the standalone HTML file"""
    return send_from_directory('.', 'standalone_chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if len(message) > 5000:  # Prevent extremely long messages
            return jsonify({'error': 'Message too long. Please keep it under 5000 characters.'}), 400
        
        response = get_response(message, session_id)
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"[ERROR] Chat endpoint error: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500

@app.route('/clear', methods=['POST'])
def clear_chat():
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default') if data else 'default'
        
        if session_id in conversation_history:
            conversation_history[session_id] = [SYSTEM_PROMPT]
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[ERROR] Clear endpoint error: {str(e)}")
        return jsonify({'error': 'Failed to clear chat'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AVExpert Chatbot',
        'version': '2.0.0'
    })

if __name__ == '__main__':
    print("🚗 Starting AV-OS - Autonomous Vehicle Intelligence...")
    print("=" * 60)
    
    # Test API connection
    print("� Testing Groq API connection...")
    try:
        test_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ Groq API connection successful!")
    except Exception as e:
        print(f"⚠️  Groq API connection failed: {str(e)[:100]}...")
        print("📝 The app will still run in offline mode with built-in AV responses.")
        print("🔧 Check your internet connection and API key for full functionality.")
    
    print(f"📡 Server starting at: http://localhost:5000")
    print(f"🎨 Premium Interface: http://localhost:5000")
    print("🔑 Make sure your GROQ_API_KEY is set in the .env file")
    print("=" * 60)
    
    # Enable CORS for development (optional)
    try:
        from flask_cors import CORS
        CORS(app)
        print("✅ CORS enabled for cross-origin requests")
    except ImportError:
        print("⚠️  flask-cors not installed (optional - continuing without CORS)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)