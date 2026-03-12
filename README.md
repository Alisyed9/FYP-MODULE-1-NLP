# NLP Threat Classifier - Web Application

A comprehensive web-based application for multi-class threat classification using a Bidirectional LSTM neural network. Users can classify security threats from text or batch process files.

## Features

### Module 1: Direct Text Classification 📝
- Real-time text classification
- Supports single tweet or threat text input
- Instant results with confidence scores
- Named Entity Recognition (NER) integration
- Probability distribution across all threat classes

### Module 2: Batch File Processing 📂
- Upload and process multiple texts at once
- Supports: `.xlsx` (Excel), `.csv`, `.txt` file formats
- Drag-and-drop file upload
- Bulk classification with statistics
- Download results as CSV

## Threat Classes
The model classifies threats into 6 categories:
- **Phishing** - Credential harvesting attacks
- **Ransomware** - Encrypted data/extortion threats
- **Malware** - Malicious software distribution
- **Botnet** - Automated attack networks
- **Virus** - Self-propagating malware
- **Benign** - Non-threatening content

## Project Structure

```
nlp-model/
├── nlp_pipeline.py              # Original training script
├── app.py                       # Flask web server
├── requirements.txt             # Python dependencies
├── templates/
│   └── index.html              # Web UI
├── threat_model_output/        # Trained model & artifacts
│   ├── Bidirectional_LSTM_ThreatClassifier.h5
│   ├── tokenizer.pkl
│   ├── label_encoder.pkl
│   ├── model_meta.pkl
│   └── classification_report.xlsx
├── uploads/                    # Temporary file upload directory
├── nlp-env/                    # Python virtual environment
└── Tweets_with_Confidence_Scores.xlsx
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- 1GB free disk space (for model weights)

### Step 1: Install Dependencies

Activate the virtual environment:
```bash
cd c:\Users\Admin\Documents\nlp-model
nlp-env\Scripts\Activate.ps1
```

Install required packages:
```bash
pip install -r requirements.txt
```

Download spaCy language model (required for NER):
```bash
python -m spacy download en_core_web_sm
```

### Step 2: Start the Flask Application

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Step 3: Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

## API Endpoints

### 1. **GET** `/api/health`
Check if the model is loaded and get available threat classes
```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "online",
  "model_loaded": true,
  "threat_classes": ["Phishing", "Ransomware", "Malware", "Botnet", "Virus", "Benign"]
}
```

### 2. **POST** `/api/classify`
Classify a single text
```bash
curl -X POST http://localhost:5000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Your threat text here"}'
```

Response:
```json
{
  "success": true,
  "threat_type": "Phishing",
  "confidence": 0.9543,
  "generalized_text": "...",
  "entities": [["Google", "ORG"]],
  "all_predictions": {
    "Phishing": 0.9543,
    "Ransomware": 0.0312,
    "Malware": 0.0089,
    "Botnet": 0.0034,
    "Virus": 0.0019,
    "Benign": 0.0003
  }
}
```

### 3. **POST** `/api/upload`
Upload and process a file (xlsx, csv, or txt)
```bash
curl -X POST -F "file=@tweets.csv" http://localhost:5000/api/upload
```

Response:
```json
{
  "success": true,
  "total_processed": 50,
  "results": [
    {
      "threat_type": "Phishing",
      "confidence": 0.9543,
      "row_index": 0,
      "original_text": "...",
      ...
    }
  ]
}
```

### 4. **POST** `/api/batch`
Classify multiple texts in one request
```bash
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["text1", "text2", "text3"]}'
```

## Usage Examples

### Example 1: Direct Text Classification
1. Go to **Module 1: Direct Text Classification**
2. Paste a tweet or threat text in the textarea
3. Click **Classify Text**
4. View results with confidence scores and threat probabilities

### Example 2: Batch File Processing
1. Go to **Module 2: Batch File Processing**
2. Upload a CSV file with a "text" column
3. Click **Upload & Process**
4. Download results as CSV when complete

### Example 3: Using with Python
```python
import requests
import json

# Direct text classification
response = requests.post('http://localhost:5000/api/classify', 
    json={'text': 'Your threat text here'})
result = response.json()

print(f"Threat Type: {result['threat_type']}")
print(f"Confidence: {result['confidence'] * 100:.2f}%")
print(f"All Predictions: {result['all_predictions']}")
```

## Model Architecture

**Bidirectional LSTM Classifier**
- Input: Tokenized text sequences (max_length dynamic)
- Embedding Layer: 10-dimensional embeddings (vocab_size: 5000)
- Bidirectional LSTM: 64 units (processes text forwards and backwards)
- Dense Layer: 64 units with ReLU activation (feature extraction)
- Output Layer: Softmax over 6 threat classes
- Loss: Sparse Categorical Crossentropy
- Optimizer: Adam
- Epochs: 10
- Batch Size: 32

## Performance

View the model's classification report:
- Open `threat_model_output/classification_report.xlsx`
- Contains precision, recall, F1-score per threat class

## Text Preprocessing

The model applies the following preprocessing steps:

1. **Generalization**
   - Replace mentions (@username) with `<NAME>`
   - Replace hashtags (#topic) with `<HASHTAG>`
   - Replace URLs with `<URL>`
   - Replace organization names with `<ORG>`

2. **Named Entity Recognition**
   - Extracts: PERSON, ORG, GPE, DATE, TIME, PRODUCT, etc.
   - Displayed in results for context

3. **Tokenization & Padding**
   - Converts text to sequences of integers
   - Pads to maximum sequence length

## Troubleshooting

### Issue: Model not loading
```bash
# Verify model files exist
dir threat_model_output/
# Expected files:
# - Bidirectional_LSTM_ThreatClassifier.h5
# - tokenizer.pkl
# - label_encoder.pkl
# - model_meta.pkl
```

### Issue: Port 5000 already in use
```bash
# Change port in app.py
# app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Issue: CORS errors in browser
The Flask-CORS extension handles cross-origin requests automatically.

### Issue: Out of memory on large files
The app processes files sequentially to conserve memory. For files > 10MB, consider splitting them.

## Configuration

Edit `app.py` to modify:

```python
# Maximum file size (default: 16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Upload folder
UPLOAD_FOLDER = 'uploads'

# Supported file types
ALLOWED_EXTENSIONS = {'xlsx', 'csv', 'txt'}

# Flask settings
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Browser Compatibility

- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Performance Tips

1. **For 100+ texts**: Use the batch file upload instead of direct input
2. **Large files**: Split into multiple uploads (< 5MB each)
3. **High throughput**: Deploy with production WSGI server (Gunicorn, etc.)

## Future Enhancements

- [ ] Multi-language support
- [ ] Real-time processing dashboard
- [ ] Model retraining endpoint
- [ ] Confidence threshold filtering
- [ ] API authentication (API keys)
-  [ ] Database storage for audit logging
- [ ] Export to JSON, SQLite formats
- [ ] Advanced analytics & visualizations

## License

Internal Use - TactiKoolSec

## Support

For issues or questions, check the model training script logs:
```bash
# Review training history
python nlp_pipeline.py
```

---

**Happy Threat Classifying! 🚀**
