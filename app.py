import sys
import traceback
import tempfile
import os
import json
import requests
import yaml

from flask import Flask, request, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from waitress import serve
from datetime import datetime
from urllib.parse import urlparse

from restful_checker.engine.analyzer import analyze_api

app = Flask(__name__)
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

limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute", "100 per day"])

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return Response(status=200)

    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Received /analyze request from {request.remote_addr} | User-Agent: {request.headers.get('User-Agent')}")

    try:
        if not request.data:
            return {"error": "No input provided"}, 400

        input_raw = request.data.decode('utf-8')
        ext = ".json"

        body = request.get_json(silent=True)
        if isinstance(body, dict) and "url" in body:
            url = body["url"]
            if not url.endswith(('.json', '.yaml', '.yml')):
                return {"error": "Only .json, .yaml or .yml URLs are allowed"}, 400

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                input_raw = response.text
                ext = ".yaml" if url.endswith(('.yaml', '.yml')) else ".json"
            except Exception as e:
                return {"error": f"Failed to fetch URL: {str(e)}"}, 400

        # Validate that the content is a valid JSON or YAML object (dict)
        try:
            parsed = json.loads(input_raw) if ext == ".json" else yaml.safe_load(input_raw)
            if not isinstance(parsed, dict):
                return {"error": f"Invalid content: expected a JSON/YAML object (dict), got {type(parsed).__name__}"}, 400
        except Exception:
            return {"error": f"Invalid content for extension {ext}"}, 400

        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix=ext, encoding='utf-8') as f:
            f.write(input_raw)
            f.flush()
            input_path = f.name

        result = analyze_api(input_path, output_dir="html")

        with open(result["html_path"], 'r', encoding='utf-8') as f:
            html = f.read()

        os.remove(input_path)
        os.remove(result["html_path"])

        return Response(html, mimetype='text/html')

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 53127))
    print(f">>> Flask server starting on port {port}")
    serve(app, host='0.0.0.0', port=port)