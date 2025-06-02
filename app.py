import sys
import traceback
import tempfile
import os
import json

from flask import Flask, request, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from waitress import serve
from flask import Flask, request
from datetime import datetime

from restful_checker.engine.analyzer import analyze_api

app = Flask(__name__)

# 🔒 Limit max request size to 2 MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# 🔒 Allow CORS from both Vercel and local development environments
# CORS(app, resources={
#     r"/analyze": {
#         "origins": [
#             "https://restful-checker-website.vercel.app",  # ✅ your deployed frontend
#             "http://localhost:3000",                        # 🧪 local development
#             "http://127.0.0.1:3000",                        # 🧪 local dev (loopback)
#             "http://192.168.1.*"                            # 🧪 local network for friends/testing
#         ]
#     }
# })

# ⚠️ TEMPORARY DEBUG CONFIGURATION
# Allow CORS from any origin — for testing purposes only
# Do NOT use this in production environments
CORS(app)

# 🔒 Rate limiting to prevent abuse
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute", "100 per day"])

@app.route('/analyze', methods=['POST'])
def analyze():

    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Received /analyze request from {request.remote_addr} | User-Agent: {request.headers.get('User-Agent')}")

    try:
        if not request.data:
            return {"error": "No input provided"}, 400

        # ✅ Validate input is a valid JSON
        try:
            json.loads(request.data.decode('utf-8'))
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}, 400

        # ✅ Save JSON to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json', encoding='utf-8') as f:
            f.write(request.data.decode('utf-8'))
            f.flush()
            input_path = f.name

        # ✅ Run the RESTful analysis (only HTML)
        result = analyze_api(input_path, output_dir="html")

        # ✅ Read the generated HTML report
        with open(result["html_path"], 'r', encoding='utf-8') as f:
            html = f.read()

        # ✅ Clean up temporary files
        os.remove(input_path)
        os.remove(result["html_path"])

        # ✅ Return the HTML content as a response
        return Response(html, mimetype='text/html')

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 53127))
    print(f">>> Flask server starting on port {port}")
    serve(app, host='0.0.0.0', port=port)