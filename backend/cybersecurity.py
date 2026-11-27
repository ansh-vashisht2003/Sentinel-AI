
import re
from typing import Any


# ==========================================================
# SENTINEL AI - CYBERSECURITY RULE ENGINE
# Message-based threat detection using regex and if-else
# ==========================================================

RULES = [
    {
        "name": "OTP Theft",
        "category": "Credential Theft",
        "weight": 25,
        "patterns": [
            r"\b(share|send|forward|tell|provide|reveal|enter|submit)\b.{0,45}\b(otp|one[- ]time password|verification code|login code)\b",
            r"\b(otp|one[- ]time password|verification code)\b.{0,45}\b(share|send|forward|tell|provide|reveal|submit)\b",
        ],
        "reason": "The message attempts to obtain an OTP or verification code."
    },
    {
        "name": "Password and PIN Theft",
        "category": "Credential Theft",
        "weight": 25,
        "patterns": [
            r"\b(share|send|provide|reveal|tell|enter|submit)\b.{0,45}\b(password|passwd|upi pin|atm pin|cvv|passcode)\b",
            r"\b(password|upi pin|atm pin|cvv|passcode)\b.{0,45}\b(share|send|provide|reveal|submit)\b",
        ],
        "reason": "The message requests confidential authentication or banking credentials."
    },
    {
        "name": "Financial Fraud",
        "category": "Payment Fraud",
        "weight": 20,
        "patterns": [
            r"\b(send|transfer|pay|deposit)\b.{0,45}\b(money|cash|amount|rupees|rs\.?|inr|upi)\b",
            r"\b(pay|transfer|deposit)\b.{0,35}\b(fee|charges|tax|processing|registration)\b",
            r"\b(advance payment|processing fee|claim fee|refund fee)\b",
            r"\b(send money|transfer money|make payment|pay now)\b",
        ],
        "reason": "The message contains a potentially fraudulent payment or money-transfer request."
    },
    {
        "name": "Threat and Intimidation",
        "category": "Social Engineering",
        "weight": 20,
        "patterns": [
            r"\b(account|sim|card|number)\b.{0,35}\b(blocked|suspended|deactivated|terminated)\b",
            r"\b(arrest|police action|legal action|lawsuit|fine|penalty)\b",
            r"\b(you will be arrested|we will block|account will be closed)\b",
            r"\b(last warning|final warning|serious consequences)\b",
        ],
        "reason": "The message uses threats or intimidation to pressure the recipient."
    },
    {
        "name": "Urgency Manipulation",
        "category": "Social Engineering",
        "weight": 12,
        "patterns": [
            r"\b(immediately|urgent|right now|act now|hurry|without delay)\b",
            r"\b(within \d+ minutes|within \d+ hours|today only|expires today)\b",
            r"\b(verify immediately|respond immediately|limited time)\b",
        ],
        "reason": "The message creates artificial urgency to influence the recipient's decision."
    },
    {
        "name": "Personal Information Theft",
        "category": "Identity Theft",
        "weight": 20,
        "patterns": [
            r"\b(send|share|provide|upload|submit)\b.{0,50}\b(aadhaar|aadhar|pan card|passport|date of birth|bank details)\b",
            r"\b(send|share|provide|reveal)\b.{0,40}\b(address|identity proof|account number|personal details)\b",
        ],
        "reason": "The message requests sensitive personal or identity information."
    },
    {
        "name": "Fake Prize and Reward",
        "category": "Reward Fraud",
        "weight": 15,
        "patterns": [
            r"\b(you have won|you are a winner|congratulations.{0,30}won)\b",
            r"\b(claim your prize|claim your reward|lottery winner|free gift)\b",
            r"\b(lucky draw|cash prize|prize money|reward points)\b",
        ],
        "reason": "The message uses a prize or reward offer that may be designed to lure the recipient."
    },
    {
        "name": "Impersonation",
        "category": "Identity Deception",
        "weight": 15,
        "patterns": [
            r"\b(we are from|i am from|calling from)\b.{0,40}\b(bank|police|government|support|customer care)\b",
            r"\b(bank officer|bank representative|official support team|government officer)\b",
            r"\b(rbi|income tax department|customs department)\b.{0,50}\b(verify|pay|submit|share|update)\b",
        ],
        "reason": "The message may be impersonating an organisation or authority."
    },
    {
        "name": "Remote Access Manipulation",
        "category": "Device Compromise",
        "weight": 25,
        "patterns": [
            r"\b(install|download)\b.{0,40}\b(anydesk|teamviewer|remote access|apk)\b",
            r"\b(enable|allow|give)\b.{0,30}\b(screen sharing|remote access)\b",
            r"\b(control your phone|access your device remotely)\b",
        ],
        "reason": "The message requests remote device access or installation of potentially unsafe software."
    },
    {
        "name": "Secrecy and Blackmail",
        "category": "Coercion",
        "weight": 20,
        "patterns": [
            r"\b(don't tell anyone|do not tell anyone|keep this secret|tell nobody)\b",
            r"\b(blackmail|pay or else|leak your photos|leak your information)\b",
            r"\b(we will expose you|we will publish|we will leak)\b",
        ],
        "reason": "The message uses secrecy, coercion or blackmail tactics."
    },
    {
        "name": "Suspicious Link",
        "category": "Phishing Indicator",
        "weight": 10,
        "patterns": [
            r"https?://[^\s]+",
            r"\bwww\.[^\s]+",
        ],
        "reason": "The message contains a link. Its safety has not been verified."
    },
    {
        "name": "Shortened URL",
        "category": "Phishing Indicator",
        "weight": 15,
        "patterns": [
            r"\b(bit\.ly|tinyurl\.com|t\.co|goo\.gl|cutt\.ly|rb\.gy)/[^\s]+",
        ],
        "reason": "The message contains a shortened URL that hides its final destination."
    }
]


def analyze_cybersecurity_message(message: str) -> dict[str, Any]:

    message = (message or "").strip()

    if not message:
        raise ValueError("Message cannot be empty.")

    findings = []
    total_score = 0
    detected_categories = set()

    # Check every cybersecurity rule
    for rule in RULES:

        matched = False

        for pattern in rule["patterns"]:

            if re.search(pattern, message, flags=re.IGNORECASE):
                matched = True
                break

        if matched:

            # Prevent duplicate scoring for the same rule
            if rule["name"] not in detected_categories:

                findings.append({
                    "indicator": rule["name"],
                    "category": rule["category"],
                    "points": rule["weight"],
                    "reason": rule["reason"]
                })

                total_score += rule["weight"]
                detected_categories.add(rule["name"])

    # Calculate cybersecurity score
    cybersecurity_score = min(total_score, 100)

    # Determine risk level
    if cybersecurity_score >= 70:
        risk_level = "High Risk"

    elif cybersecurity_score >= 35:
        risk_level = "Medium Risk"

    elif cybersecurity_score > 0:
        risk_level = "Low Risk"

    else:
        risk_level = "No Rules Triggered"

    # Generate explanations
    if findings:

        reasons = [
            finding["reason"]
            for finding in findings
        ]

        classification = "Suspicious"

    else:

        reasons = [
            "No configured cybersecurity rules were triggered."
        ]

        classification = "No Threat Indicators Detected"

    # Extract URLs for optional future reputation checks
    urls = re.findall(
        r"(?:https?://|www\.)[^\s<>()]+",
        message,
        flags=re.IGNORECASE
    )

    return {
    "success": True,
    "engine": "SENTINEL AI Cybersecurity Engine",

    # Keys required by whatsapp.py
    "score": cybersecurity_score,
    "urls": urls,

    # Detailed cybersecurity report
    "cybersecurity_threat_score": cybersecurity_score,
    "risk_level": risk_level,
    "classification": classification,
    "total_rules_triggered": len(findings),
    "detected_categories": list(
        dict.fromkeys(
            finding["category"] for finding in findings
        )
    ),
    "findings": findings,
    "reasons": reasons,
    "urls_found": urls
}
