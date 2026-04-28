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

def get_response(message, session_id):
    """Get response from Groq API with improved error handling"""
    try:
        # Initialize conversation history for new sessions
        if session_id not in conversation_history:
            conversation_history[session_id] = [SYSTEM_PROMPT]
        
        # Add user message
        conversation_history[session_id].append({"role": "user", "content": message})
        
        # Get AI response with better error handling
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
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
        error_msg = f"API Error: {str(e)}"
        print(f"[ERROR] {error_msg}")  # Log error for debugging
        
        # Return user-friendly error message
        if "rate limit" in str(e).lower():
            return "⚠️ Rate limit exceeded. Please wait a moment and try again."
        elif "api key" in str(e).lower():
            return "🔑 API key issue. Please check your Groq API key configuration."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            return "🌐 Network connection issue. Please check your internet connection."
        else:
            return f"❌ Sorry, I encountered an error: {str(e)[:100]}..."

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
    print("🚗 Starting AVExpert - Autonomous Vehicle AI Chatbot...")
    print("=" * 60)
    print(f"📡 Server running at: http://localhost:5000")
    print(f"🎨 Premium Interface: http://localhost:5000")
    print(f"📱 Standalone Version: http://localhost:5000/standalone")
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