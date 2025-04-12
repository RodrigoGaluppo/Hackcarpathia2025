import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import os
import sys

# Add the current directory to the path to find model_params.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the parameters from the generated file
try:
    from model_params import vectorizer_vocabulary, vectorizer_params, nb_params
    print("Successfully imported model parameters")
except ImportError as e:
    print(f"Error importing model_params: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Files in directory: {os.listdir(current_dir)}")
    raise

class SpamClassifier:
    def __init__(self):
        print("Initializing SpamClassifier...")
        
        # Create a copy of vectorizer_params without the 'vocabulary' key
        # This prevents passing 'vocabulary' twice
        safe_params = {}
        for key, value in vectorizer_params.items():
            # Skip 'vocabulary' and other parameters that might cause issues
            if key != 'vocabulary' and key not in ['dtype', 'encoding', 'input']:
                safe_params[key] = value
        
        # Initialize and configure the vectorizer from saved parameters
        self.vectorizer = CountVectorizer(
            vocabulary=vectorizer_vocabulary,
            **safe_params
        )
        
        # Initialize and configure the Naive Bayes model from saved parameters
        self.model = MultinomialNB()
        
        # Ensure proper data types for NumPy arrays
        self.model.class_count_ = np.array(nb_params['class_count'], dtype=np.float64)
        self.model.class_log_prior_ = np.array(nb_params['class_log_prior'], dtype=np.float64)
        self.model.classes_ = np.array(nb_params['classes'], dtype=np.int64)
        self.model.feature_count_ = np.array(nb_params['feature_count'], dtype=np.float64)
        self.model.feature_log_prob_ = np.array(nb_params['feature_log_prob'], dtype=np.float64)
        
        print("SpamClassifier initialized successfully")
        
    def predict(self, input_data):
        # Accept either a DataFrame or list of texts
        import pandas as pd
        if isinstance(input_data, pd.DataFrame):
            texts = input_data.iloc[:, 0].tolist()  # assumes text is in the first column
        elif isinstance(input_data, list):
            texts = input_data
        elif isinstance(input_data, str):
            texts = [input_data]
        else:
            raise ValueError("Input must be a pandas DataFrame, list of strings, or a single string")
        
        try:
            # Vectorize the input texts
            X = self.vectorizer.transform(texts)
            
            # Make predictions
            predictions = self.model.predict(X)
            probabilities = self.model.predict_proba(X)
            
            # Format results
            results = []
            for i in range(len(texts)):
                results.append({
                    "text": texts[i],
                    "label": "spam" if predictions[i] == 1 else "safe",
                    "confidence": round(float(max(probabilities[i])) * 100, 2)
                })
                
            return results
        except Exception as e:
            print(f"Error during prediction: {e}")
            # Return a simple error message for each text
            return [{"text": text, "label": "error", "confidence": 0, "error": str(e)} for text in texts]

# For testing
if __name__ == "__main__":
    try:
        classifier = SpamClassifier()
        test_messages = [
            "Your account has been compromised. Click here to reset your password.",
            "Hi Jane, can we meet at 3 PM tomorrow?"
        ]
        results = classifier.predict(test_messages)
        print("Test predictions:")
        for result in results:
            print(f"{result['text']} -> {result['label']} ({result['confidence']}%)")
    except Exception as e:
        print(f"Error during testing: {e}")