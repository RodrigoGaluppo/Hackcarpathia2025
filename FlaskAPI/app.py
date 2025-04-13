# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from tools.virustotal import VirusTotalClient
import os
from dotenv import load_dotenv
import sys

load_dotenv()
app = Flask(__name__)
CORS(app)

# Initialize tool clients
vt_client = VirusTotalClient(os.getenv("VIRUSTOTAL_API_KEY"))


# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the SpamClassifier
try:
    from tools.spamclassifier import SpamClassifier
    print("Successfully imported SpamClassifier")
except ImportError as e:
    print(f"Error importing SpamClassifier: {e}")
    raise


# Initialize the classifier
try:
    classifier = SpamClassifier()
    print("SpamClassifier initialized in app.py")
except Exception as e:
    print(f"Error initializing SpamClassifier: {e}")
    raise

@app.route('/api/scan', methods=['POST'])
def scan_url():
    
    data = request.get_json()
    
    response = {
        "malicious_count": 0,
        "malicious_reports": {
            "BitDefender": {
                "category": "malicious",
                "engine_name": "BitDefender",
                "method": "blacklist",
                "result": "malware"
            },
            "CRDF": {
                "category": "malicious",
                "engine_name": "CRDF",
                "method": "blacklist",
                "result": "malicious"
            },
            "CyRadar": {
                "category": "malicious",
                "engine_name": "CyRadar",
                "method": "blacklist",
                "result": "malicious"
            },
            "Fortinet": {
                "category": "malicious",
                "engine_name": "Fortinet",
                "method": "blacklist",
                "result": "malware"
            },
            "G-Data": {
                "category": "malicious",
                "engine_name": "G-Data",
                "method": "blacklist",
                "result": "malware"
            },
            "Lionic": {
                "category": "malicious",
                "engine_name": "Lionic",
                "method": "blacklist",
                "result": "malware"
            },
            "Sophos": {
                "category": "malicious",
                "engine_name": "Sophos",
                "method": "blacklist",
                "result": "malware"
            },
            "alphaMountain.ai": {
                "category": "malicious",
                "engine_name": "alphaMountain.ai",
                "method": "blacklist",
                "result": "malicious"
            }
        },
        "suspicious_count": 0,
        "url": "http://jetblue.com-offers.host/"
    }


    if not data or 'url' not in data:
        return jsonify({"error": "Missing URL parameter"}), 400
    
    try:
        result = vt_client.analyze_url(data['url'])

        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    if not data or 'messages' not in data:
        return jsonify({'error': 'No messages provided'}), 400
    
    messages = data['messages']
    results = classifier.predict(messages)
    
    return jsonify({'predictions': results})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=("localhost+2.pem", "localhost+2-key.pem"))
