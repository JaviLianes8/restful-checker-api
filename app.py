import sys
import traceback
import tempfile
import os
import json

from flask import Flask, request, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from restful_checker.engine.analyzer import analyze_api

app = Flask(__name__)

# 🔒 Limit max request size to 2 MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# 🔒 Allow CORS only from the official frontend
CORS(app, resources={r"/analyze": {"origins": "https://restful-checker-website.vercel.app"}})

# 🔒 Rate limit per IP to prevent abuse
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute", "100 per day"])

@app.route('/analyze', methods=['POST'])
def analyze():
    print("[DEBUG] /analyze endpoint hit")
    print(f"[DEBUG] Python path: {sys.executable}")

    try:
        if not request.data:
            return {"error": "No input provided"}, 400

        # ✅ Validate input is a valid JSON
        try:
            json.loads(request.data.decode('utf-8'))
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}, 400

        # ✅ Save JSON to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json') as f:
            f.write(request.data.decode('utf-8'))
            f.flush()
            input_path = f.name

        # ✅ Run the RESTful analysis
        result_path = analyze_api(input_path)

        # ✅ Read the generated HTML report
        with open(result_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # ✅ Clean up temporary files
        os.remove(input_path)
        os.remove(result_path)

        # ✅ Return the HTML content as a response
        return Response(html, mimetype='text/html')

    except Exception as e:
        # ❌ Log unexpected errors
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    # 🔧 Load port from env variable
    port = int(os.getenv("PORT", 53127))
    print(f">>> Flask server starting on port {port}")
    app.run(host="0.0.0.0", port=port)