from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import pickle
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'csv', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Load Model and Resources
try:
    with open('threat_model_output/model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    with open('threat_model_output/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    
    with open('threat_model_output/model_meta.pkl', 'rb') as f:
        model_meta = pickle.load(f)
    
    print("[OK] Model and resources loaded successfully")
    print(f"[OK] Model type: {model_meta.get('model_type', 'sklearn')}")
except Exception as e:
    print(f"[ERROR] Loading model: {str(e)}")

# Utility Functions
def generalize(text):
    """Generalize text similar to preprocessing"""
    text = str(text)
    text = re.sub(r"@\w+", "<NAME>", text)
    text = re.sub(r"#\w+", "<HASHTAG>", text)
    text = re.sub(r"http\S+|www\S+", "<URL>", text)
    text = re.sub(r"\b(Google|Microsoft|IBM|Cloudflare|Cisco|Amazon|TactiKoolSec)\b",
                  "<ORG>", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()

def classify_text(text):
    """Classify a single text using hybrid approach: keywords + ML model"""
    try:
        # Generalize the text
        generalized_text = generalize(text)
        text_lower = str(text).lower()
        
        # Define keyword patterns for high-precision detection
        # XSS & CODE INJECTION - HIGHEST PRIORITY
        xss_keywords = ['<script', 'javascript:', 'onerror=', 'onload=', 
                       'onclick=', 'onmouseover=', 'onanimationstart=',
                       'style=', 'iframe', 'eval(', 'alert(', '<img', 'svg']
        
        threat_keywords = {
            'Malware': xss_keywords + ['trojan', 'backdoor', 'rootkit', 'spyware', 'adware', 'worm'],
            'Ransomware': ['encrypted', 'encrypt', 'ransom', 'btc', 'bitcoin', 'wallet', 'decrypt', 'locked'],
            'Botnet': ['botnet', 'ddos', 'distributed denial', 'command control'],
            'Virus': ['virus', 'replicate', 'propagat', 'self-replicate'],
            'Phishing': ['phishing', 'phish', 'verify account', 'confirm account', 'verify your', 
                        'confirm your', 'unusual activity', 'suspended', 'urgent', 'immediately',
                        'verify identity', 'secure link', 'click here', 're-activate']
        }
        
        # Check for keywords (keyword matching path) - XSS/Malware gets highest priority
        keyword_match = None
        is_xss = any(kw in text_lower for kw in xss_keywords)
        
        if is_xss:
            # XSS detected - very high confidence
            keyword_match = 'Malware'
        else:
            # Check other threats in order
            for threat_type, keywords in threat_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    keyword_match = threat_type
                    break
        
        # Get ML model prediction
        ml_prediction = model.predict([generalized_text])[0]
        ml_probabilities = model.predict_proba([generalized_text])[0]
        ml_confidence = float(np.max(ml_probabilities))
        
        # Hybrid decision: XSS always gets priority, others depend on confidence
        if is_xss:
            # XSS detection - shows as XSS threat type
            final_prediction = 'XSS'
            final_confidence = 0.95
        elif keyword_match and ml_confidence < 0.65:
            # Use keyword match when ML confidence is low
            final_prediction = keyword_match
            final_confidence = 0.85
        else:
            # Use ML model prediction
            final_prediction = ml_prediction
            final_confidence = ml_confidence
        
        # Get all class probabilities
        all_preds = {
            label_encoder.classes_[i]: round(float(ml_probabilities[i]), 4)
            for i in range(len(label_encoder.classes_))
        }
        
        return {
            'success': True,
            'threat_type': final_prediction,
            'confidence': round(final_confidence, 4),
            'generalized_text': generalized_text,
            'entities': extract_named_entities(text),
            'all_predictions': all_preds,
            'detection_method': 'xss-detected' if is_xss else ('keyword-hybrid' if keyword_match else 'ml-model')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def extract_named_entities(text):
    """Extract named entities from text"""
    # Simple entity extraction based on patterns
    entities = []
    entity_patterns = [
        (r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', 'PERSON'),  # Names
        (r'(?:Google|Microsoft|IBM|Amazon|Cloudflare|Cisco)\b', 'ORG'),  # Organizations
    ]
    
    for pattern, label in entity_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            entities.append((match.group(0), label))
    
    return entities

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    """Serve the homepage"""
    return render_template('index.html')

@app.route('/api/classify', methods=['POST'])
def classify():
    """Classify text from user input"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        result = classify_text(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Process uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed. Use .xlsx, .csv, or .txt'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file
        if filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            results = [classify_text(text)]
        else:
            df = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)
            
            # Look for text column
            text_column = None
            for col in df.columns:
                if col.lower() in ['text', 'tweet', 'content', 'raw tweet', 'generalized tweet']:
                    text_column = col
                    break
            
            if text_column is None:
                text_column = df.columns[0]  # Use first column if no match
            
            # Classify each row
            results = []
            for idx, row in df.iterrows():
                text = str(row[text_column])
                result = classify_text(text)
                result['row_index'] = idx
                result['original_text'] = text
                results.append(result)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'total_processed': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/batch', methods=['POST'])
def batch_classify():
    """Classify multiple texts from user input"""
    try:
        data = request.json
        texts = data.get('texts', [])
        
        if not texts or not isinstance(texts, list):
            return jsonify({'success': False, 'error': 'Invalid texts format'}), 400
        
        results = []
        for idx, text in enumerate(texts):
            text = str(text).strip()
            if text:
                result = classify_text(text)
                result['index'] = idx
                results.append(result)
        
        return jsonify({
            'success': True,
            'total_processed': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'model_loaded': True,
        'threat_classes': list(label_encoder.classes_)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
