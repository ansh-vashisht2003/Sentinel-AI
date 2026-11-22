from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import logging

# WhatsApp engine
from whatsapp import (
    analyze_whatsapp_message,
    train_and_select_model,
    get_model_comparison
)

# SMS engine
from sms import (
    analyze_sms_message,
    train_and_select_sms_model,
    get_sms_model_comparison
)

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

# CORS CONFIGURATION
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [frontend_origin] if frontend_origin != "*" else "*"
        }
    },
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

logging.basicConfig(level=logging.INFO)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():
    return jsonify({
        "success": True,
        "service": "SENTINEL AI",
        "modules": ["WhatsApp", "SMS"]
    }), 200


# ==================================================
# WHATSAPP
# ==================================================

@app.post("/api/whatsapp/analyze")
def analyze_whatsapp():

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
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

    except Exception:
        app.logger.exception("WhatsApp analysis failed")

        return jsonify({
            "success": False,
            "error": "WhatsApp analysis failed. Check backend logs."
        }), 500


@app.post("/api/whatsapp/train")
def train_whatsapp():

    try:
        result = train_and_select_model()

        return jsonify({
            "success": True,
            **result
        }), 200

    except Exception as exc:
        app.logger.exception("WhatsApp training failed")

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@app.get("/api/whatsapp/models")
def whatsapp_models():

    try:
        result = get_model_comparison()

        return jsonify({
            "success": True,
            **result
        }), 200

    except Exception as exc:
        app.logger.exception("WhatsApp model comparison failed")

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@app.post("/api/whatsapp/extract")
def extract_whatsapp_screenshot():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No screenshot file supplied."
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "success": False,
            "error": "Choose a screenshot first."
        }), 400

    allowed = {".png", ".jpg", ".jpeg", ".webp"}

    ext = Path(secure_filename(file.filename)).suffix.lower()

    if ext not in allowed:
        return jsonify({
            "success": False,
            "error": "Only PNG, JPG, JPEG, and WEBP images are supported."
        }), 400

    try:
        from PIL import Image
        import pytesseract
        import io

        image = Image.open(
            io.BytesIO(file.read())
        ).convert("RGB")

        extracted = pytesseract.image_to_string(image).strip()

        return jsonify({
            "success": True,
            "extracted_text": extracted,
            "message": "Review OCR text before analysis; OCR can make mistakes."
        }), 200

    except ImportError:
        return jsonify({
            "success": False,
            "error": "Install Pillow, pytesseract and Tesseract OCR."
        }), 500

    except Exception:
        app.logger.exception("OCR extraction failed")

        return jsonify({
            "success": False,
            "error": "Could not extract text from this image."
        }), 500


# ==================================================
# SMS
# ==================================================

@app.post("/api/sms/analyze")
def analyze_sms():

    data = request.get_json(silent=True) or {}

    try:
        result = analyze_sms_message(
            message=data.get("message", ""),
            mobile_number=data.get("mobile_number"),
            country_code=data.get("country_code")
        )

        return jsonify(result), 200

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

    except Exception:
        app.logger.exception("SMS analysis failed")

        return jsonify({
            "success": False,
            "error": "SMS analysis failed. Check backend terminal logs."
        }), 500


@app.post("/api/sms/train")
def train_sms():

    try:
        result = train_and_select_sms_model()

        return jsonify({
            "success": True,
            **result
        }), 200

    except Exception as exc:
        app.logger.exception("SMS model training failed")

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@app.get("/api/sms/models")
def sms_models():

    try:
        result = get_sms_model_comparison()

        return jsonify({
            "success": True,
            **result
        }), 200

    except Exception as exc:
        app.logger.exception("SMS model comparison failed")

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


# ==================================================
# RUN SERVER
# ==================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )
