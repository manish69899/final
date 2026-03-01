import os
import logging
from flask import Flask
from threading import Thread

# Flask server ko initialize kar rahe hain
app = Flask('')

# Server ke logs ko thoda clean rakhne ke liye warning level set kiya hai
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Ye pura HTML, CSS, aur JavaScript code hai jo browser me render hoga
# Isme Matrix effect aur neon hacker theme add ki gayi hai
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARYAN's Bot Terminal</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: #000;
            color: #0f0;
            font-family: 'Fira Code', monospace;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        /* Matrix Background Canvas */
        canvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
        }

        /* Main Content Box */
        .terminal-box {
            position: relative;
            z-index: 1;
            background: rgba(0, 10, 0, 0.85);
            border: 2px solid #0f0;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px #0f0, inset 0 0 20px #0f0;
            text-align: center;
            max-width: 600px;
            width: 90%;
            backdrop-filter: blur(5px);
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-transform: uppercase;
            text-shadow: 0 0 10px #0f0;
            animation: glitch 1.5s infinite;
        }

        .status {
            font-size: 1.2rem;
            margin: 20px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        /* Pulsing Dot Animation */
        .dot {
            width: 15px;
            height: 15px;
            background-color: #0f0;
            border-radius: 50%;
            box-shadow: 0 0 10px #0f0, 0 0 20px #0f0;
            animation: pulse 1.5s infinite alternate;
        }

        .details {
            font-size: 0.9rem;
            color: #88ff88;
            margin-top: 20px;
            text-align: left;
            border-top: 1px dashed #0f0;
            padding-top: 20px;
            line-height: 1.6;
        }

        .aryan-highlight {
            color: #fff;
            text-shadow: 0 0 10px #fff, 0 0 20px #0f0, 0 0 30px #0f0;
            font-size: 1.5rem;
            font-weight: bold;
            display: inline-block;
            margin-top: 15px;
            animation: float 3s ease-in-out infinite;
        }

        /* Animations */
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(1.3); opacity: 1; }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }

        @keyframes glitch {
            0% { text-shadow: 0.05em 0 0 rgba(255,0,0,.75), -0.05em -0.025em 0 rgba(0,255,0,.75), -0.025em 0.05em 0 rgba(0,0,255,.75); }
            14% { text-shadow: 0.05em 0 0 rgba(255,0,0,.75), -0.05em -0.025em 0 rgba(0,255,0,.75), -0.025em 0.05em 0 rgba(0,0,255,.75); }
            15% { text-shadow: -0.05em -0.025em 0 rgba(255,0,0,.75), 0.025em 0.025em 0 rgba(0,255,0,.75), -0.05em -0.05em 0 rgba(0,0,255,.75); }
            49% { text-shadow: -0.05em -0.025em 0 rgba(255,0,0,.75), 0.025em 0.025em 0 rgba(0,255,0,.75), -0.05em -0.05em 0 rgba(0,0,255,.75); }
            50% { text-shadow: 0.025em 0.05em 0 rgba(255,0,0,.75), 0.05em 0 0 rgba(0,255,0,.75), 0 -0.05em 0 rgba(0,0,255,.75); }
            99% { text-shadow: 0.025em 0.05em 0 rgba(255,0,0,.75), 0.05em 0 0 rgba(0,255,0,.75), 0 -0.05em 0 rgba(0,0,255,.75); }
            100% { text-shadow: -0.025em 0 0 rgba(255,0,0,.75), -0.025em -0.025em 0 rgba(0,255,0,.75), -0.025em -0.05em 0 rgba(0,0,255,.75); }
        }
    </style>
</head>
<body>

    <!-- Matrix Animation Canvas -->
    <canvas id="matrixCanvas"></canvas>

    <!-- Main Content -->
    <div class="terminal-box">
        <h1>SYSTEM ONLINE</h1>
        
        <div class="status">
            <div class="dot"></div>
            <span>Bot is Alive & Running 24/7</span>
        </div>

        <div class="details">
            <p>> INITIALIZING PROTOCOLS... <span style="color:#fff;">[OK]</span></p>
            <p>> ESTABLISHING SECURE CONNECTION... <span style="color:#fff;">[OK]</span></p>
            <p>> BYPASSING MAINFRAME... <span style="color:#fff;">[OK]</span></p>
            <br>
            <p style="text-align: center;">ROOT ACCESS GRANTED TO:</p>
        </div>

        <div class="aryan-highlight">
            &lt; ARYAN /&gt;
        </div>
    </div>

    <!-- Matrix Digital Rain Script -->
    <script>
        const canvas = document.getElementById('matrixCanvas');
        const ctx = canvas.getContext('2d');

        // Screen size set karna
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Matrix ke liye characters
        const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレゲゼデベペオォコソトノホモヨョロゴゾドボポヴッン';
        const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const nums = '0123456789';
        const alphabet = katakana + latin + nums;

        const fontSize = 16;
        const columns = canvas.width / fontSize;

        const rainDrops = [];

        // Har column ke liye drop initialize karna
        for (let x = 0; x < columns; x++) {
            rainDrops[x] = 1;
        }

        const draw = () => {
            // Background me thoda black shade daalna taaki trail effect aaye
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#0F0'; // Hacker Green Text
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < rainDrops.length; i++) {
                const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                
                // Character draw karna
                ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);

                // Drop ko reset karna jab bottom me pahuch jaye
                if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    rainDrops[i] = 0;
                }
                rainDrops[i]++;
            }
        };

        // Animation loop
        setInterval(draw, 30);

        // Window resize handle karna
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Plain text ki jagah ab pura animated HTML render hoga
    return HTML_CONTENT

def run():
    # Render, Heroku ya Replit jo port assign karega wo use hoga, default 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """
    Ek alag thread mein Flask server chalata hai
    taaki aapka main bot block na ho.
    """
    t = Thread(target=run)
    t.start()