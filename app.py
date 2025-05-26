import sys
import traceback
from flask import Flask, request, Response
import tempfile
from restful_checker.core.analyzer import analyze_api

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    print("[DEBUG] /analyze endpoint HIT")
    print(f"[DEBUG] Python path: {sys.executable}")
    try:
        if not request.data:
            print("[DEBUG] No data received")
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
    print(">>> Flask server starting")
    app.run()