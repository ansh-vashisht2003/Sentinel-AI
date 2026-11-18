# SENTINEL AI WhatsApp backend

## Windows setup
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```
Install Tesseract OCR separately and add `tesseract.exe` to PATH.

## Train the model
```powershell
python train_model.py --csv "C:\\path\\to\\sentinel_whatsapp_ai_cybersecurity_training_1000.csv"
```
This creates `models/whatsapp_model.joblib`.

## Run
```powershell
python app.py
```
API endpoints:
- GET `/api/health`
- POST `/api/whatsapp/extract` multipart field `file`
- POST `/api/whatsapp/analyze` JSON:
`{"message":"...","source":"text","country_code":"+91","mobile_number":"9876543210"}`

## Required Vue change
Your attached Vue component declares `country_code` and `mobile_number` but currently does not send them. In `analyzeMessage()`, replace the JSON body with:
```ts
body: JSON.stringify({
  message: message.value,
  source: mode.value,
  country_code: country_code.value,
  mobile_number: mobile_number.value
})
```
Render `result.reasons` as objects using `reason.engine` and `reason.reason`. Also show `result.engine_scores.aiml_threat_score`, `result.engine_scores.cybersecurity_threat_score`, `result.phone_intelligence`, and `result.phone_number_activity.sentinel_investigation_count`.

## Important limitations
- The score is a heuristic index (60% ML + 40% cybersecurity), not a calibrated probability. Calibrate on representative independent data before presenting it as probability.
- Your 1,000-row dataset is synthetic demonstration data. Do not claim real-world accuracy from its metrics.
- Phone reputation remains Unknown until a lawful provider is configured. Adapt the provider adapter to its documented response format.
- WhatsApp does not provide private login/access counts from a phone number. The count returned is only SENTINEL's own investigation count.
- URL reputation remains Unknown; current code extracts URLs but does not query a reputation service.
- Production requires authentication, rate limits, HTTPS, secret management, consent, encryption, retention/deletion controls and audit logging.
