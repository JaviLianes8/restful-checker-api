import os
import shutil
import sys
import traceback
import uuid
import tempfile
import multiprocessing
import json
import warnings

from flask import Flask, request, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from waitress import serve
from datetime import datetime
from restful_checker.main import main

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

CORS(app)

# Oculta el warning del backend en memoria
warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits*")

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["5 per minute", "100 per day"]
)

def run_checker(input_arg, output_dir):
    sys.argv = ["restful-checker", input_arg, "--output-format", "html", "--output-folder", output_dir]
    main()

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return Response(status=200)

    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Received /analyze request from {request.remote_addr} | User-Agent: {request.headers.get('User-Agent')}")

    tmp_file_path = None
    output_dir = None

    try:
        if not request.data:
            return {"error": "No input provided"}, 400

        body = request.get_json(silent=True)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "temp", str(uuid.uuid4()))
        os.makedirs(output_dir, exist_ok=True)

        if isinstance(body, dict) and "url" in body:
            input_arg = body["url"]
        else:
            file_data = request.get_data(as_text=True).strip()
            if not file_data:
                return {"error": "Empty input"}, 400

            try:
                json.loads(file_data)
            except Exception:
                return {"error": "Invalid JSON input"}, 400

            with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json', encoding='utf-8') as tmp_file:
                tmp_file.write(file_data)
                tmp_file.flush()
                tmp_file_path = tmp_file.name
                input_arg = tmp_file_path

        p = multiprocessing.Process(target=run_checker, args=(input_arg, output_dir))
        p.start()
        p.join(timeout=10)

        if p.is_alive():
            p.terminate()
            p.join()
            return {"error": "Timeout: analysis took too long"}, 504

        html_path = os.path.join(output_dir, "rest_report.html")
        if not os.path.exists(html_path):
            return {"error": "Invalid input or OpenAPI file could not be analyzed."}, 400

        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        return Response(html_content, mimetype='text/html')

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        if output_dir and os.path.exists(output_dir):
            shutil.rmtree(output_dir)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    port = int(os.getenv("PORT", 53127))
    print(f">>> Flask server starting on port {port}")
    serve(app, host='0.0.0.0', port=port)