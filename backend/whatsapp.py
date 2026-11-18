"""
SENTINEL AI - WhatsApp module
AI/ML and cybersecurity engines are kept separate.
AI/ML = message classification + threat category + explainable text signals.
Cybersecurity = transparent rules + anomaly detection + optional reputation lookups.
Final score = 50% AI/ML + 50% Cybersecurity.

Important:
- The included CSVs are synthetic/demo data, not verified threat intelligence.
- The model confidence is an estimated score, not a calibrated real-world probability.
- Outlier/anomaly detection means unusual compared with training data; it does not mean malicious.
"""
from __future__ import annotations

import os
import re
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import ExtraTreesClassifier, IsolationForest, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier, PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.naive_bayes import MultinomialNB, ComplementNB, BernoulliNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATASET_PATH = Path(os.getenv("WHATSAPP_DATASET", PROJECT_DIR / "datasets" / "whatsapp_master" / "whatsapp_message_dataset_500.csv"))
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "whatsapp_aiml_model.joblib"
METRICS_PATH = MODEL_DIR / "model_comparison.json"
DB_PATH = BASE_DIR / "whatsapp_history.db"
logger = logging.getLogger("sentinel.whatsapp")

# These are deliberately transparent rules, not claims about private WhatsApp account data.
RULES = {
    "otp_or_verification_code": (r"\b(otp|one[- ]time password|verification code|login code)\b", 18,
        "The message mentions an OTP or verification code."),
    "asks_for_pin_or_password": (r"\b(upi pin|pin number|password|passcode|cvv|card number|bank details)\b", 25,
        "The message asks for a sensitive PIN, password, or financial credential."),
    "payment_or_advance_fee": (r"\b(pay|payment|transfer|send money|upi|advance fee|processing fee|refund fee)\b", 16,
        "The message contains a payment or money-transfer request."),
    "urgent_or_threatening_language": (r"\b(urgent|immediately|within \d+ minutes|account blocked|account suspended|act now|last warning)\b", 12,
        "The message uses urgency or threat language."),
    "prize_or_reward_lure": (r"\b(won|winner|prize|lottery|gift card|claim reward|free gift)\b", 12,
        "The message uses a prize, lottery, or reward lure."),
    "impersonation": (r"\b(customer support|bank officer|police|government|delivery agent|official team|we are from)\b", 10,
        "The sender appears to claim an organisation or authority identity."),
    "remote_access_or_app_install": (r"\b(anydesk|teamviewer|remote access|screen sharing|install this app|download apk)\b", 20,
        "The message asks for remote access, screen sharing, or app installation."),
    "secrecy_or_coercion": (r"\b(don't tell|do not tell|keep this secret|secretly|you will be arrested|legal action)\b", 12,
        "The message uses secrecy, coercion, or intimidation."),
    "suspicious_link": (r"(https?://|www\.)", 8,
        "The message contains a link that should be checked before opening."),
    "shortened_link": (r"\b(bit\.ly|tinyurl\.com|t\.co|goo\.gl|cutt\.ly|rb\.gy)/", 12,
        "The message contains a URL-shortening domain."),
}
THREAT_LABELS = {"malicious", "phishing", "fraud", "scam", "credential"}

def _normalise_label(value: Any) -> str:
    return "Malicious" if str(value).strip().lower() in THREAT_LABELS else (
        "Malicious" if str(value).strip().lower() == "malicious" else "Benign"
    )

def _make_models():
    # All models operate on the same TF-IDF representation.
    # Calibrated linear models provide a usable confidence-like score.
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1500, class_weight="balanced"),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.5),
        "Complement Naive Bayes": ComplementNB(alpha=0.5),
        "Bernoulli Naive Bayes": BernoulliNB(alpha=0.5),
        "Random Forest": RandomForestClassifier(n_estimators=250, class_weight="balanced", random_state=42, n_jobs=-1),
        "Extra Trees": ExtraTreesClassifier(n_estimators=250, class_weight="balanced", random_state=42, n_jobs=-1),
        "Decision Tree": DecisionTreeClassifier(class_weight="balanced", random_state=42, max_depth=30),
        "SGD Log-Loss": SGDClassifier(loss="log_loss", max_iter=2000, class_weight="balanced", random_state=42),
        "Calibrated Linear SVC": CalibratedClassifierCV(LinearSVC(class_weight="balanced", random_state=42), cv=3),
        "Calibrated Passive Aggressive": CalibratedClassifierCV(PassiveAggressiveClassifier(class_weight="balanced", random_state=42, max_iter=2000), cv=3),
    }
    return models

def train_and_select_model(dataset_path: str | Path = DATASET_PATH) -> dict:
    """Train/compare 10 algorithms and save the best pipeline + anomaly detector."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(
            f"WhatsApp dataset not found: {path}. Put whatsapp_message_dataset_500.csv "
            "inside datasets/whatsapp_master/ or set WHATSAPP_DATASET."
        )
    import csv
    def load_whatsapp_dataset(path):
        encodings = ["utf-8-sig", "utf-8", "latin1"]
        delimiters = [",", "\t", ";", "|"]

        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    df = pd.read_csv(
                        path,
                        sep=delimiter,
                        encoding=encoding,
                        engine="python",
                        skipinitialspace=True,
                        on_bad_lines="error"
                    )

                    df.columns = (
                        df.columns.astype(str)
                        .str.strip()
                        .str.replace("\ufeff", "", regex=False)
                    )

                    if "message" in df.columns and "label" in df.columns:
                        print("\nDataset loaded successfully!")
                        print("Encoding:", encoding)
                        print("Delimiter:", repr(delimiter))
                        print("Total records:", len(df))
                        print("Columns:", df.columns.tolist())

                        return df

                except Exception:
                    continue

        raise ValueError(
            "Dataset format could not be identified. "
            "Check the CSV header and delimiter."
        )


    df = load_whatsapp_dataset(path)
    required = {"message", "label"}
    if not required.issubset(df.columns):
        raise ValueError(f"Dataset must contain columns: {sorted(required)}. Found: {list(df.columns)}")
    df = df.dropna(subset=["message", "label"]).copy()
    df["message"] = df["message"].astype(str).str.strip()
    df = df[df["message"].str.len() > 0]
    df["target"] = df["label"].map(_normalise_label)
    if df["target"].nunique() != 2 or df["target"].value_counts().min() < 5:
        raise ValueError("Need at least 5 examples of both Benign and Malicious labels.")

    # Only message text is used as a model feature. suspicious_reason and threat_category
    # are intentionally excluded because they can leak the answer into the model.
    X = df["message"].values
    y = df["target"].values
    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(
        lowercase=True, strip_accents="unicode", ngram_range=(1, 2),
        min_df=1, max_features=25000, sublinear_tf=True,
        token_pattern=r"(?u)\b\w+\b"
    )
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    # Stratified CV ranks algorithms using macro-F1; the holdout test is reported separately.
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results, fitted = [], {}
    for name, estimator in _make_models().items():
        try:
            scores = cross_val_score(estimator, x_train_vec, y_train, cv=cv, scoring="f1_macro", n_jobs=None)
            model = clone(estimator)
            model.fit(x_train_vec, y_train)
            pred = model.predict(x_test_vec)
            row = {
                "model": name,
                "cv_macro_f1_mean": round(float(scores.mean()), 4),
                "cv_macro_f1_std": round(float(scores.std()), 4),
                "holdout_accuracy": round(float(accuracy_score(y_test, pred)), 4),
                "holdout_precision_macro": round(float(precision_score(y_test, pred, average="macro", zero_division=0)), 4),
                "holdout_recall_macro": round(float(recall_score(y_test, pred, average="macro", zero_division=0)), 4),
                "holdout_macro_f1": round(float(f1_score(y_test, pred, average="macro", zero_division=0)), 4),
            }
            results.append(row)
            fitted[name] = model
        except Exception as exc:
            logger.exception("Could not train %s", name)
            results.append({"model": name, "error": str(exc)})

    valid = [r for r in results if "error" not in r]
    if not valid:
        raise RuntimeError("None of the 10 candidate models trained successfully.")
    # Select on CV macro-F1, not holdout score, to avoid tuning on the test set.
    best_row = max(valid, key=lambda r: r["cv_macro_f1_mean"])
    best_name = best_row["model"]
    best_model = fitted[best_name]

    # Outlier detector: reduce sparse TF-IDF to a compact semantic feature space.
    # It is a separate anomaly signal and is NOT a malicious/benign classifier.
    svd_components = max(2, min(100, x_train_vec.shape[1] - 1, x_train_vec.shape[0] - 1))
    svd = TruncatedSVD(n_components=svd_components, random_state=42)
    train_reduced = svd.fit_transform(x_train_vec)
    anomaly_detector = IsolationForest(
        n_estimators=200, contamination="auto", random_state=42
    ).fit(train_reduced)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    bundle = {
        "vectorizer": vectorizer,
        "model": best_model,
        "model_name": best_name,
        "svd": svd,
        "anomaly_detector": anomaly_detector,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "classes": list(best_model.classes_),
    }
    joblib.dump(bundle, MODEL_PATH)
    metrics = {
        "selected_model": best_name,
        "selection_metric": "5-fold cross-validation macro-F1",
        "dataset_rows": int(len(df)),
        "train_rows": int(len(x_train)),
        "holdout_rows": int(len(x_test)),
        "warning": "Synthetic dataset; scores are prototype diagnostics, not real-world validation.",
        "model_comparison": sorted(valid, key=lambda r: r["cv_macro_f1_mean"], reverse=True),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics

def _load_bundle():
    if not MODEL_PATH.exists():
        train_and_select_model()
    return joblib.load(MODEL_PATH)

def _probability_for_malicious(bundle, message: str) -> tuple[float, str]:
    vec = bundle["vectorizer"].transform([message])
    model = bundle["model"]
    probs = model.predict_proba(vec)[0]
    classes = list(model.classes_)
    idx = classes.index("Malicious") if "Malicious" in classes else int(np.argmax(probs))
    return float(probs[idx] * 100), str(model.predict(vec)[0])

def _rule_engine(message: str) -> dict:
    findings = []
    points = 0
    for key, (pattern, weight, explanation) in RULES.items():
        if re.search(pattern, message, flags=re.IGNORECASE):
            points += weight
            findings.append({"indicator": key, "points": weight, "reason": explanation})
    # Multiple matches can raise score, capped at 100.
    score = min(100.0, float(points))
    urls = re.findall(r"(?:https?://|www\.)[^\s<>()]+", message, flags=re.IGNORECASE)
    return {"score": round(score, 2), "findings": findings, "urls": urls}

def _anomaly_score(bundle, message: str) -> dict:
    vec = bundle["vectorizer"].transform([message])
    reduced = bundle["svd"].transform(vec)
    detector = bundle["anomaly_detector"]
    raw = float(detector.decision_function(reduced)[0])
    is_outlier = int(detector.predict(reduced)[0]) == -1
    # Small bounded contribution; anomaly is contextual, not evidence of fraud.
    score = 15.0 if is_outlier else 0.0
    return {"is_unusual": is_outlier, "anomaly_score": round(score, 2),
            "explanation": "Message differs from the training-message patterns." if is_outlier
            else "No strong text-pattern anomaly detected.", "raw_detector_value": round(raw, 5)}

def _phone_intelligence(mobile_number: str | None, country_code: str | None) -> dict:
    # No fabricated reputation. Add a real provider adapter only when credentials/API are configured.
    if not mobile_number:
        return {"status": "not_provided", "reputation": "unknown",
                "note": "No phone number was supplied."}
    return {"status": "provider_not_configured", "reputation": "unknown",
            "note": "No verified phone-reputation provider is configured. This is not a safe/unsafe verdict.",
            "number_suffix": str(mobile_number)[-4:]}

def _url_intelligence(urls: list[str]) -> dict:
    if not urls:
        return {"status": "no_url_found", "items": []}
    return {"status": "provider_not_configured",
            "items": [{"url": u, "reputation": "unknown",
                       "note": "No live URL reputation provider is configured."} for u in urls]}

def _save_investigation(payload: dict) -> int:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            mobile_number TEXT,
            country_code TEXT,
            message TEXT NOT NULL,
            final_score REAL NOT NULL,
            verdict TEXT NOT NULL,
            report_json TEXT NOT NULL
        )""")
        cur = con.execute(
            "INSERT INTO investigations(created_at,mobile_number,country_code,message,final_score,verdict,report_json) VALUES(?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), payload.get("mobile_number"),
             payload.get("country_code"), payload["message"], payload["final_threat_score"],
             payload["verdict"], json.dumps(payload, ensure_ascii=False))
        )
        return int(cur.lastrowid)

def get_investigation_count(mobile_number: str | None, country_code: str | None = None) -> int:
    if not mobile_number or not DB_PATH.exists():
        return 0
    with sqlite3.connect(DB_PATH) as con:
        row = con.execute(
            "SELECT COUNT(*) FROM investigations WHERE mobile_number=? AND COALESCE(country_code,'')=COALESCE(?, '')",
            (str(mobile_number), country_code)
        ).fetchone()
    return int(row[0]) if row else 0

def analyze_whatsapp_message(message: str, mobile_number: str | None = None,
                             country_code: str | None = None, source: str = "paste") -> dict:
    message = (message or "").strip()
    if not message:
        raise ValueError("Message text is empty.")
    if len(message) > 10000:
        raise ValueError("Message exceeds the 10,000-character limit.")

    bundle = _load_bundle()
    ai_score, predicted_label = _probability_for_malicious(bundle, message)
    rules = _rule_engine(message)
    anomaly = _anomaly_score(bundle, message)

    # Cybersecurity score is transparent: 85% rule indicators + 15% anomaly signal.
    cyber_score = min(100.0, 0.85 * rules["score"] + 0.15 * anomaly["anomaly_score"])
    final_score = round(0.50 * ai_score + 0.50 * cyber_score, 2)
    verdict = ("High Risk" if final_score >= 75 else
               "Medium Risk" if final_score >= 40 else "Low Risk")

    # Explain AI output using matched language signals. Avoid claiming a specific feature attribution
    # from TF-IDF, which this model does not calculate.
    ai_reasons = []
    if predicted_label == "Malicious":
        ai_reasons.append("The selected ML model classifies the message as Malicious based on learned text patterns.")
    else:
        ai_reasons.append("The selected ML model classifies the message as Benign based on learned text patterns.")
    ai_reasons.append(f"Selected model: {bundle['model_name']}. Its score is a model confidence-like estimate, not a calibrated probability.")
    cybersecurity_reasons = [x["reason"] for x in rules["findings"]]
    if anomaly["is_unusual"]:
        cybersecurity_reasons.append(anomaly["explanation"])
    if not cybersecurity_reasons:
        cybersecurity_reasons.append("No configured cybersecurity rule was triggered.")

    phone_info = _phone_intelligence(mobile_number, country_code)
    url_info = _url_intelligence(rules["urls"])
    report = {
        "success": True,
        "module": "whatsapp",
        "final_threat_score": final_score,
        "threat_percentage": final_score,
        "verdict": verdict,
        "score_method": "50% AI/ML + 50% Cybersecurity",
        "engine_scores": {
            "aiml_threat_score": round(ai_score, 2),
            "cybersecurity_threat_score": round(cyber_score, 2),
            "weights": {"aiml": 0.5, "cybersecurity": 0.5}
        },
        "aiml_engine": {
            "prediction": predicted_label,
            "threat_category": "Not separately predicted by this binary model",
            "selected_model": bundle["model_name"],
            "confidence_score": round(ai_score, 2),
            "reasons": ai_reasons
        },
        "cybersecurity_engine": {
            "rule_score": rules["score"],
            "anomaly": anomaly,
            "findings": rules["findings"],
            "reasons": cybersecurity_reasons,
            "urls_found": rules["urls"]
        },
        "phone_intelligence": phone_info,
        "url_intelligence": url_info,
        "recommended_actions": (
            ["Do not reply, click links, share OTP/PIN/passwords, or transfer money.",
             "Verify the sender using an independently obtained official contact channel.",
             "Report/block the sender if the message is confirmed fraudulent."]
            if final_score >= 40 else
            ["Do not share OTPs, PINs, or passwords, even if the message appears normal.",
             "Verify unexpected links or requests through an official channel."]
        ),
        "disclaimer": "Prototype risk score based on synthetic training data and configured rules; not proof that a sender or number is malicious.",
        "model_metadata": {"trained_at": bundle.get("trained_at"), "source": str(DATASET_PATH)},
        "source": source
    }
    before = get_investigation_count(mobile_number, country_code)
    report["phone_number_activity"] = {
        "sentinel_investigation_count_before_this_scan": before,
        "sentinel_investigation_count_including_this_scan": before + 1,
        "note": "This counts SENTINEL investigations only; it is not WhatsApp login or account-access history."
    }
    report["investigation_id"] = _save_investigation({"message": message, **report,
                                                       "mobile_number": mobile_number,
                                                       "country_code": country_code})
    return report

def get_model_comparison() -> dict:
    if not METRICS_PATH.exists():
        return train_and_select_model()
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
