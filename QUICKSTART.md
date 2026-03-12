# Quick Start Guide

## Option 1: Using Batch Script (Easiest for Windows)

1. **Double-click** `run.bat` in the project folder
2. The script will automatically:
   - Activate the virtual environment
   - Install/update dependencies
   - Download the spaCy language model
   - Start the Flask server
3. Open your browser and go to: **http://localhost:5000**
4. Press `CTRL+C` in the terminal to stop the server

## Option 2: Using PowerShell

1. **Right-click PowerShell** and select "Run as Administrator"
2. Navigate to the project folder:
   ```powershell
   cd C:\Users\Admin\Documents\nlp-model
   ```
3. Run the startup script:
   ```powershell
   .\run.ps1
   ```
4. Open your browser and go to: **http://localhost:5000**

## Option 3: Manual Setup

1. Activate the virtual environment:
   ```bash
   nlp-env\Scripts\Activate.bat
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. Run the Flask app:
   ```bash
   python app.py
   ```

## What You'll See

After running the startup script, you should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
 * WARNING in production!
```

## Accessing the Application

### Local Machine
```
http://localhost:5000
```

### From Another Computer on Network
```
http://<YOUR_COMPUTER_IP>:5000
```

Find your computer's IP:
```powershell
ipconfig
# Look for "IPv4 Address" under your network adapter
```

## Features

### Module 1: Direct Text Classification 📝
- Type or paste text
- Click "Classify Text"
- Get instant threat classification with confidence score

### Module 2: Batch File Processing 📂
- Drag & drop CSV/Excel/Text files
- Process multiple samples at once
- Download results as CSV

## Example Inputs

**Phishing Example:**
"Click here to verify your Google account credentials: [link]"

**Malware Example:**
"Download trojan.exe for free! Infected with latest malware"

**Ransomware Example:**
"Your files are encrypted! Send bitcoin to unlock"

## Troubleshooting

### Port 5000 in Use
If you get "Address already in use" error:
1. Edit `app.py` (last line)
2. Change `port=5000` to `port=5001`
3. Save and run again
4. Access at `http://localhost:5001`

### Module Not Found Error
Run this command:
```bash
pip install --upgrade tensorflow keras spacy scikit-learn pandas
```

### spaCy Model Error
```bash
python -m spacy download en_core_web_sm
```

## File Upload Requirements

**Supported Formats:**
- CSV (.csv) - First column should be text
- Excel (.xlsx) - First column should be text
- Text (.txt) - Plain text file

**File Size:** Maximum 16MB per file

**Column Format:** If using CSV/Excel, the first column (or a column named "text", "tweet", "content") will be processed.

## Getting Help

1. Check the [README.md](README.md) for detailed documentation
2. Review [app.py](app.py) for API endpoints
3. Check Flask error logs in the terminal

---

**Happy Classifying! 🚀**
