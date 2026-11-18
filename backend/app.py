from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import logging

from whatsapp import analyze_whatsapp_message, train_and_select_model, get_model_comparison

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB screenshot limit
CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})
logging.basicConfig(level=logging.INFO)

@app.get("/api/health")
def health():
    return jsonify({"success": True, "service": "SENTINEL AI WhatsApp API"})

@app.post("/api/whatsapp/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    try:
        result = analyze_whatsapp_message(
            message=data.get("message", ""),
            mobile_number=data.get("mobile_number"),
            country_code=data.get("country_code"),
            source=data.get("source", "paste")
        )
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 500
    except Exception:
        app.logger.exception("WhatsApp analysis failed")
        return jsonify({"success": False, "error": "Analysis failed. Check backend terminal logs."}), 500

@app.post("/api/whatsapp/train")
def train():
    # Protect this endpoint in production; do not expose model retraining publicly.
    try:
        return jsonify({"success": True, **train_and_select_model()}), 200
    except Exception as exc:
        app.logger.exception("Model training failed")
        return jsonify({"success": False, "error": str(exc)}), 500

@app.get("/api/whatsapp/models")
def models():
    try:
        return jsonify({"success": True, **get_model_comparison()}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

@app.post("/api/whatsapp/extract")
def extract():
    """OCR endpoint for uploaded screenshots. Requires pytesseract + local Tesseract binary."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No screenshot file supplied."}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"success": False, "error": "Choose a screenshot first."}), 400
    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    ext = Path(secure_filename(file.filename)).suffix.lower()
    if ext not in allowed:
        return jsonify({"success": False, "error": "Only PNG, JPG, JPEG, and WEBP images are supported."}), 400
    try:
        from PIL import Image
        import pytesseract
        import io
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
        extracted = pytesseract.image_to_string(image).strip()
        return jsonify({"success": True, "extracted_text": extracted,
                        "message": "Review OCR text before analysis; OCR can make mistakes."}), 200
    except ImportError:
        return jsonify({"success": False, "error": "Install Pillow and pytesseract, and install the Tesseract OCR application."}), 500
    except Exception:
        app.logger.exception("OCR extraction failed")
        return jsonify({"success": False, "error": "Could not extract text from this image."}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
