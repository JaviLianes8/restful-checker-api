import sys
import traceback
import tempfile

from restful_checker.core.analyzer import analyze_api
from flask_cors import CORS
from flask import Flask, request, Response

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    print("[DEBUG] /analyze endpoint HIT")
    print(f"[DEBUG] Python path: {sys.executable}")
    try:
        if not request.data:
            print("[DEBUG] No data received ")
            return {"error": "No input provided"}, 400

        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json') as f:
            f.write(request.data.decode('utf-8'))
            f.flush()
            input_path = f.name

        result_path = analyze_api(input_path)
        print(f"[DEBUG] HTML generated at: {result_path}")

        with open(result_path, 'r', encoding='utf-8') as f:
            html = f.read()

        return Response(html, mimetype='text/html')

    except Exception as e:
        print("[ERROR] Exception caught:")
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    from os import getenv
    port = int(getenv("PORT", 10000))
    print(f">>> Flask server starting on port {port}")
    app.run(host="0.0.0.0", port=port)