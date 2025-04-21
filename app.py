from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Configure the API key
GOOGLE_API_KEY = 'AIzaSyAchd8_DSU-SwKIFxXSdFeljocMJqenrSI'
genai.configure(api_key=GOOGLE_API_KEY)

# Load the model
model = genai.GenerativeModel("gemini-2.0-flash")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Virtual Museum Guide</title>
    <link href="https://i1.wp.com/worldupclose.in/wp-content/uploads/2020/03/taj.jpg" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #6b4d9c;
            --secondary-color: #8b5e99;
            --background-color: #e8f0f3;
            --text-color: #333;
        }

        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            position: relative;
            background: linear-gradient(rgba(232, 240, 243, 0.5), rgba(232, 240, 243, 0.5)),
            url('https://images.unsplash.com/photo-1564507592333-c60657eea523?ixlib=rb-1.2.1&auto=format&fit=crop&w=1951&q=80');

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        header > div {
            flex: 1;
        }

        header .center-title{
            text-align: center;
        }

        header img {
            height: 60px;
            border-radius: 10px;
        }

        header h1 {
            color: var(--primary-color);
            font-size: 1.6em;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        header p {
            color: #666;
            margin-top: 5px;
        }

        .profile-info {
            text-align: right;
        }

        .profile-info div {
            margin: 2px 0;
            font-size: 0.95em;
            color: #444;
        }

    
            .chat-container {
            background: rgba(255, 255, 255, 0.85);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .chat-header {
            background: var(--primary-color);
            color: white;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chat-header i {
            font-size: 1.2em;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            background: #4CAF50;
            border-radius: 50%;
            margin-left: auto;
        }

        #chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
        }

        .message {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 10px;
            max-width: 80%;
        }

        .bot-message {
            background: var(--primary-color);
            color: white;
            align-self: flex-start;
            margin-right: auto;
        }

        .user-message {
            background: var(--secondary-color);
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }

        .chat-input {
            display: flex;
            padding: 15px;
            gap: 10px;
            background: #f5f5f5;
            border-top: 1px solid #eee;
        }

        #user-input {
            flex-grow: 1;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
        }

        .chat-input button {
            background: var(--button-color);
            color: black;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-input button:hover {
            background: var(--secondary-color);
        }
    </style>
</head>
<body>
    <div class="container">
       <header>
    <!-- Left: Logo -->
    <div style="text-align: left;">
        <img src="/static/logo.png" alt="Logo">
    </div>

    <!-- Center: Title -->
    <div class="center-title">
        <h1><i class="fas fa-landmark"></i>Museum Guide</h1>
        <p>Your virtual guide to world heritage sites</p>
    </div>

    <!-- Right: Profile Info -->
    <div class="profile-info">
        <div><strong>Taman Preet Singh</strong></div>
        <div>Reg No: 12309438</div>
        <div>Teacher: Mr. Anurag Singh</div>
    </div>
</header>


        <div class="chat-container">
            <div class="chat-header">
                <i class="fas fa-robot"></i>
                <span>Museum Guide</span>
                <div class="status-indicator"></div>
            </div>

            <div id="chat-messages">
                <div class="message bot-message">
                    Welcome to the Virtual Museum Guide! I can tell you about historical artifacts, 
                    famous monuments like the Indian Museum , Taj Mahal and answer your questions about world heritage. 
                    How can I assist you today?
                </div>
            </div>

            <div class="chat-input">
                <input type="text" id="user-input" placeholder="Ask about any historical artifact or monument...">
                <button onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    </div>

   <script>
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;

            addMessage(message, 'user-message');
            input.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                addMessage(data.reply, 'bot-message');
            } catch (error) {
                addMessage('Sorry, I encountered an error. Please try again.', 'bot-message');
            }
        }

        function addMessage(message, className) {
            const chatMessages = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + className;
            messageDiv.textContent = message;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    try:
        response = model.generate_content(message)
        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    