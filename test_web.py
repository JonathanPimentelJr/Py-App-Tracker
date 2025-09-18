#!/usr/bin/env python3
"""
Simple test web server to verify Flask is working correctly.
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Py-App-Tracker Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 50px;
                background-color: #f0f0f0;
            }
            .container {
                background: white;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                max-width: 600px;
                margin: 0 auto;
            }
            h1 { color: #007bff; }
            .success { color: #28a745; font-size: 1.2em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Py-App-Tracker Web Interface</h1>
            <p class="success">✅ Flask server is working correctly!</p>
            <p>Your web application is running successfully.</p>
            <hr>
            <p><strong>Next steps:</strong></p>
            <ul style="text-align: left;">
                <li>This confirms Flask and the web server are working</li>
                <li>The main application templates should load properly</li>
                <li>You can access the full interface once we resolve any template issues</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return {
        "status": "success",
        "message": "Web server is working",
        "flask_version": app.__dict__.get('version', 'Unknown')
    }

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Test Web Server")
    print("=" * 50)
    print("URL: http://127.0.0.1:8080")
    print("Test JSON API: http://127.0.0.1:8080/test")
    print("=" * 50)
    
    app.run(debug=True, host='127.0.0.1', port=8080)
