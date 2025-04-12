from flask import Flask, request, jsonify
import os
import sys

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the SpamClassifier
try:
    from spam_classifier import SpamClassifier
    print("Successfully imported SpamClassifier")
except ImportError as e:
    print(f"Error importing SpamClassifier: {e}")
    raise

app = Flask(__name__)

# Initialize the classifier
try:
    classifier = SpamClassifier()
    print("SpamClassifier initialized in app.py")
except Exception as e:
    print(f"Error initializing SpamClassifier: {e}")
    raise

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
    print("Starting Flask server...")
    app.run(debug=True, port=5328)
