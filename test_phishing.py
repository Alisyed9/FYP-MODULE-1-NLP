import pickle
import re

# Load the trained model
print("[LOADING] Model and encoder...")
with open('threat_model_output/model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('threat_model_output/label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

# Preprocessing function (same as in app.py)
def generalize(text):
    text = str(text)
    text = re.sub(r"@\w+", "<NAME>", text)
    text = re.sub(r"#\w+", "<HASHTAG>", text)
    text = re.sub(r"http\S+|www\S+", "<URL>", text)
    text = re.sub(r"\b(Google|Microsoft|IBM|Cloudflare|Cisco|Amazon|TactiKoolSec)\b",
                  "<ORG>", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()

# Test with the phishing email
phishing_text = """Subject: URGENT: Your Account Will Be Suspended Within 24 Hours

Dear Customer,

We detected unusual activity on your account. For your security, your access will be temporarily suspended unless you verify your information immediately.

Please confirm your account details by clicking the secure link below:

http://secure-account-verification.example.com/login

Failure to verify your account within 24 hours may result in permanent account suspension.

Thank you for your cooperation.

Security Team
Example Bank"""

print("\n" + "=" * 70)
print("PHISHING EMAIL DETECTION TEST")
print("=" * 70)

# Generalize the text
generalized = generalize(phishing_text)
print(f"\nOriginal Text Length: {len(phishing_text)} characters")
print(f"Generalized Text: {generalized[:100]}...")

# Predict
prediction = model.predict([generalized])[0]
probabilities = model.predict_proba([generalized])[0]

print("\n" + "-" * 70)
print("PREDICTION RESULTS")
print("-" * 70)
print(f"\nDetected Threat Type: [{prediction}]")
print(f"Confidence Score: {max(probabilities):.4f} ({max(probabilities)*100:.2f}%)")

print("\nAll Threat Probabilities:")
print("-" * 70)
for i, cls in enumerate(label_encoder.classes_):
    confidence_pct = probabilities[i] * 100
    bar_length = int(confidence_pct / 5)
    bar = "█" * bar_length
    print(f"  {cls:12} | {bar:20} | {probabilities[i]:.4f} ({confidence_pct:6.2f}%)")

print("-" * 70)

# Evaluation
if prediction.lower() == "phishing":
    print("\n[SUCCESS] Phishing detected correctly!")
else:
    print(f"\n[WARNING] Expected 'Phishing', got '{prediction}'")

print("=" * 70)
