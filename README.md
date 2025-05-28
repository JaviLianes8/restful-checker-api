# RESTful Checker API 🔎

**RESTful Checker API** is a lightweight Flask-based HTTP service that exposes the functionality of [`restful-checker`](https://pypi.org/project/restful-checker/) via an endpoint. You can send an OpenAPI/Swagger JSON via `POST`, and it returns an HTML report evaluating compliance with RESTful API best practices.

---

## 📦 Installation (Local)

```bash
git clone https://github.com/JaviLianes8/restful-checker-api.git
cd restful-checker-api
pip install -r requirements.txt

▶️ Run locally
python app.py
It will start on http://localhost:10000

🌍 Endpoint
POST /analyze
Submit a raw OpenAPI JSON and receive an HTML report.

Example using curl
curl -X POST http://localhost:10000/analyze \
     -H "Content-Type: application/json" \
     --data-binary @openapi.json
📥 Input: raw OpenAPI JSON
📤 Output: HTML report

🔐 CORS
CORS is enabled via flask-cors, so this API can be safely called from your frontend JavaScript app.
from flask_cors import CORS
CORS(app)

🚀 Deploy to Render
You can deploy this service easily to Render as a Web Service:

Example render.yaml
services:
  - type: web
    name: restful-checker-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py

📚 Related Projects
restful-checker (CLI tool): Python package that performs the actual validation https://github.com/JaviLianes8/restful-checker
restful-checker-ui (soon): Frontend web interface https://github.com/AlejandroSenior/restful-checker-website

🛠 Requirements
Python 3.8+
Flask
flask-cors
restful-checker

📄 License
MIT – Free to use, modify, and deploy.
