import os
import sys
import traceback
from flask import Flask, request, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from waitress import serve
from datetime import datetime
import tempfile
from restful_checker.main import main

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

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

        output_folder = "html"
        os.makedirs(output_folder, exist_ok=True)

        # Create a unique filename for the HTML report
        unique_id = os.urandom(8).hex()
        html_path = os.path.join(os.getcwd(), output_folder, f"rest_report_{unique_id}.html")

        body = request.get_json(silent=True)
        temp_file = None

        if isinstance(body, dict) and "url" in body:
            url = body["url"]
            sys.argv = ["restful-checker", url, "--output-format", "html", "--output-folder", output_folder]
            main()
        else:
            file_data = request.data.decode('utf-8')
            suffix = '.json' if file_data.strip().startswith('{') else '.yaml'
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix=suffix, encoding='utf-8')
            temp_file.write(file_data)
            temp_file.flush()
            sys.argv = ["restful-checker", temp_file.name, "--output-format", "html", "--output-folder", output_folder]
            main()

        if not os.path.exists(html_path):
            raise FileNotFoundError(f"HTML report not found at {html_path}")

        # Read the HTML file content
        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Clean up the temporary files
        if temp_file:
            os.unlink(temp_file.name)
        if os.path.exists(html_path):
            os.unlink(html_path)

        return Response(html_content, mimetype='text/html')

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 53127))
    print(f">>> Flask server starting on port {port}")
    serve(app, host='0.0.0.0', port=port)