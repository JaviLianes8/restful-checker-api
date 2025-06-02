# RESTful Checker API 🔎

**RESTful Checker API** is a lightweight Flask-based HTTP service that exposes the functionality of [`restful-checker`](https://pypi.org/project/restful-checker/) via an endpoint. You can send an OpenAPI/Swagger JSON or YAML via `POST`, and it returns an HTML report evaluating compliance with RESTful API best practices.

---

## 📦 Installation (Local)

```bash
git clone https://github.com/JaviLianes8/restful-checker-api.git
cd restful-checker-api
pip install -r requirements.txt
```

▶️ **Run locally**

```bash
python app.py
```

It will start on `http://localhost:10000`

---

## 🌍 Endpoint

**POST** `/analyze`  
Submits an OpenAPI/Swagger spec (JSON or YAML), local or remote, and returns an HTML compliance report.

---

### ✅ Input options

1. **Raw OpenAPI spec in JSON or YAML**
2. **URL to a remote OpenAPI spec (JSON or YAML)**

---

### 💡 Examples using curl

📄 Local file (JSON or YAML):
```bash
curl -X POST http://localhost:10000/analyze \
     -H "Content-Type: application/json" \
     --data-binary @openapi.yaml
```

🌐 Remote URL:
```bash
curl -X POST http://localhost:10000/analyze \
     -H "Content-Type: application/json" \
     -d '{"url":"https://petstore3.swagger.io/api/v3/openapi.yaml"}'
```

📥 Input: OpenAPI JSON or YAML  
📤 Output: HTML report

---

## 🔐 CORS

CORS is enabled using `flask-cors`, so this API can be safely consumed from frontend JavaScript apps.

```python
from flask_cors import CORS
CORS("app")
```

---

## 🚀 Deploy to Render

You can deploy this service easily to [Render](https://render.com/) as a Web Service.

### Example `render.yaml`:

```yaml
services:
  - type: web
    name: restful-checker-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
```

---

## 📚 Related Projects

- **restful-checker (CLI tool):**  
  https://github.com/JaviLianes8/restful-checker

- **restful-checker-ui (frontend):**  
  https://github.com/AlejandroSenior/restful-checker-website

---

## 🛠 Requirements

- Python 3.8+
- Flask
- flask-cors
- flask-limiter
- waitress
- restful-checker
- requests

---

## 📄 License

MIT – Free to use, modify, and deploy.

---

## 👥 Contributors

- [@alejandrosenior](https://github.com/alejandrosenior)
- [@JaviLianes8](https://github.com/JaviLianes8)

---

## ☕ Buy Me a Coffee

If you find this tool useful and want to support its development, you can buy me a coffee:

https://buymeacoffee.com/jlianesglrs
