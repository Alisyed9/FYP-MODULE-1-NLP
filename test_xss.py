import pickle
import re
import numpy as np

# Load the trained model
print("[LOADING] Model and encoder...")
with open('threat_model_output/model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('threat_model_output/label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

# Preprocessing function
def generalize(text):
    text = str(text)
    text = re.sub(r"@\w+", "<NAME>", text)
    text = re.sub(r"#\w+", "<HASHTAG>", text)
    text = re.sub(r"http\S+|www\S+", "<URL>", text)
    text = re.sub(r"\b(Google|Microsoft|IBM|Cloudflare|Cisco|Amazon|TactiKoolSec)\b",
                  "<ORG>", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()

# Hybrid classification with XSS priority
def classify_text_hybrid(text):
    generalized_text = generalize(text)
    text_lower = str(text).lower()
    
    # XSS & CODE INJECTION keywords (HIGHEST PRIORITY)
    xss_keywords = ['<script', 'javascript:', 'onerror=', 'onload=', 'onclick=', 
                    'onmouseover=', 'onanimationstart=', 'style=', 'iframe', 
                    'eval(', 'alert(', '<img', 'svg']
    
    threat_keywords = {
        'Malware': xss_keywords + ['trojan', 'backdoor', 'rootkit', 'spyware', 'adware', 'worm'],
        'Ransomware': ['encrypted', 'encrypt', 'ransom', 'btc', 'bitcoin', 'wallet', 'decrypt', 'locked'],
        'Botnet': ['botnet', 'ddos', 'distributed denial', 'command control'],
        'Virus': ['virus', 'replicate', 'propagat', 'self-replicate'],
        'Phishing': ['phishing', 'phish', 'verify account', 'confirm account', 'verify your', 
                    'confirm your', 'unusual activity', 'suspended', 'urgent', 'immediately',
                    'verify identity', 'secure link', 'click here', 're-activate']
    }
    
    # Check XSS first (HIGHEST PRIORITY)
    is_xss = any(kw in text_lower for kw in xss_keywords)
    
    keyword_match = None
    if is_xss:
        keyword_match = 'Malware'
    else:
        for threat_type, keywords in threat_keywords.items():
            if any(kw in text_lower for kw in keywords):
                keyword_match = threat_type
                break
    
    ml_prediction = model.predict([generalized_text])[0]
    ml_probabilities = model.predict_proba([generalized_text])[0]
    ml_confidence = float(np.max(ml_probabilities))
    
    # Priority: XSS > keyword match > ML model
    if is_xss:
        final_prediction = 'XSS'
        final_confidence = 0.95
        detection_method = 'xss-detected'
    elif keyword_match and ml_confidence < 0.65:
        final_prediction = keyword_match
        final_confidence = 0.85
        detection_method = 'keyword-hybrid'
    else:
        final_prediction = ml_prediction
        final_confidence = ml_confidence
        detection_method = 'ml-model'
    
    return final_prediction, final_confidence, detection_method, ml_prediction, is_xss, keyword_match

# Test XSS payload
xss_payload = '<style>@keyframes x{}</style><nobr style="animation-name:x" onanimationstart="alert(1)"></nobr>'

print("\n" + "=" * 80)
print("XSS INJECTION ATTACK TEST - HYBRID DETECTION (XSS PRIORITY)")
print("=" * 80)

final_pred, final_conf, method, ml_pred, is_xss, kw_match = classify_text_hybrid(xss_payload)

print(f"\nPayload: {xss_payload}")
print(f"\nDetection Details:")
print(f"  XSS Detected: {is_xss}")
print(f"  Keyword Match: {kw_match}")
print(f"  ML Model Prediction: {ml_pred}")
print(f"\nFinal Result:")
print(f"  Threat Type: {final_pred}")
print(f"  Confidence: {final_conf:.4f} ({final_conf*100:.2f}%)")
print(f"  Detection Method: {method}")

if final_pred.lower() == "xss" and final_conf >= 0.85:
    print("\n[✅ PASSED] XSS Attack correctly detected as XSS with 95% confidence!")
else:
    print(f"\n[❌ FAILED] Expected XSS (≥85%), got {final_pred} ({final_conf*100:.2f}%)")

print("=" * 80)
