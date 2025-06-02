import sys
import traceback
import tempfile
import os
import json
import yaml
import requests

from flask import Flask, request, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from waitress import serve
from datetime import datetime

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

def is_valid_openapi(text: str, ext: str):
    try:
        data = json.loads(text) if ext == ".json" else yaml.safe_load(text)
        return "openapi" in data or "swagger" in data
    except Exception:
        return False

@app.route('/analyze', methods=['POST'])
def analyze():
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Received /analyze request from {request.remote_addr} | User-Agent: {request.headers.get('User-Agent')}")

    try:
        if not request.data:
            return {"error": "No input provided"}, 400

        json_input = None
        ext = ".json"

        # Case 1: { "url": "https://..." }
        body = request.get_json(silent=True)
        if isinstance(body, dict) and "url" in body:
            url = body["url"]
            ext = ".yaml" if url.endswith((".yaml", ".yml")) else ".json"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                json_input = response.text
            except Exception as e:
                return {"error": f"Failed to fetch URL: {str(e)}"}, 400
        else:
            json_input = request.data.decode('utf-8')
            if json_input.lstrip().startswith("{"):
                ext = ".json"
            else:
                ext = ".yaml"

        if not is_valid_openapi(json_input, ext):
            return {"error": "Invalid or unsupported OpenAPI format"}, 400

        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix=ext, encoding='utf-8') as f:
            f.write(json_input)
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