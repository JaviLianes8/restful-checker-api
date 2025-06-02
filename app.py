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

        body = request.get_json(silent=True)

        if isinstance(body, dict) and "url" in body:
            url = body["url"]
            sys.argv = ["restful-checker", url, "--output-format", "both"]
            main()  # Running the main function from restful-checker

            # Assuming that the file is generated at a default location and read it
            with open("html/rest_report.html", "r", encoding="utf-8") as file:
                html_content = file.read()

        else:
            file_data = request.data.decode('utf-8')
            sys.argv = ["restful-checker", "--output-format", "both", "--output-folder", "html"]
            with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json', encoding='utf-8') as tmp_file:
                tmp_file.write(file_data)
                tmp_file.flush()
                sys.argv.append(tmp_file.name)
            main()

            # Reading the generated HTML file
            with open("html/rest_report.html", "r", encoding="utf-8") as file:
                html_content = file.read()

        return Response(html_content, mimetype='text/html')

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 53127))
    print(f">>> Flask server starting on port {port}")
    serve(app, host='0.0.0.0', port=port)