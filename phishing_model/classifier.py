import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
# Import the parameters from the generated file
from model_params import vectorizer_vocabulary, vectorizer_params, nb_params

class SpamClassifier:
    def __init__(self):
        # Initialize and configure the vectorizer from saved parameters
        self.vectorizer = CountVectorizer(
            vocabulary=vectorizer_vocabulary,
            **vectorizer_params
        )
        
        # Initialize and configure the Naive Bayes model from saved parameters
        self.model = MultinomialNB()
        self.model.class_count_ = np.array(nb_params['class_count'])
        self.model.class_log_prior_ = np.array(nb_params['class_log_prior'])
        self.model.classes_ = np.array(nb_params['classes'])
        self.model.feature_count_ = np.array(nb_params['feature_count'])
        self.model.feature_log_prob_ = np.array(nb_params['feature_log_prob'])
        
    def predict(self, texts):
        if isinstance(texts, str):
            texts = [texts]
            
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
