import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import re
import os

def train_and_save_model(data_path):
    # Load data
    data = pd.read_csv(data_path)
    
    # Preprocess data
    data['Spam'] = data['Category'].apply(lambda x: 1 if x == 'spam' else 0)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        data['Message'], data['Spam'], test_size=.25, random_state=25
    )
    
    # Create and train the pipeline
    vectorizer = CountVectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    
    nb_model = MultinomialNB()
    nb_model.fit(X_train_vec, y_train)
    
    # Evaluate model
    X_test_vec = vectorizer.transform(X_test)
    accuracy = nb_model.score(X_test_vec, y_test)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Define the correct directory path
    correct_directory = r"C:\Users\Administrator\PY_PROJECTS\HackCarpathia2025\Hackcarpathia2025\phishing_model"
    
    # Ensure the directory exists
    os.makedirs(correct_directory, exist_ok=True)
    
    # Define the file path
    file_path = os.path.join(correct_directory, 'model_params.py')
    
    # Save model parameters to Python file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# Auto-generated model parameters\n\n")
        
        # Save vectorizer parameters - handle non-serializable types
        f.write("# Vectorizer parameters\n")
        vectorizer_params = vectorizer.get_params()
        serializable_params = {}
        for key, value in vectorizer_params.items():
            if isinstance(value, type) or callable(value):
                serializable_params[key] = str(value)
            else:
                serializable_params[key] = value
        
        f.write("vectorizer_params = {\n")
        for key, value in serializable_params.items():
            if isinstance(value, str):
                f.write(f" '{key}': '{value}',\n")
            elif value is None:
                f.write(f" '{key}': None,\n")
            else:
                f.write(f" '{key}': {value},\n")
        f.write("}\n\n")
        
        # Save vocabulary as a dictionary
        f.write("# Vectorizer vocabulary\n")
        f.write("vectorizer_vocabulary = {\n")
        
        # Handle problematic characters in vocabulary
        for word, idx in vectorizer.vocabulary_.items():
            try:
                safe_word = re.sub(r'[^\x00-\x7F]+', '', word)
                if safe_word:
                    escaped_word = safe_word.replace("'", "\\'")
                    f.write(f" '{escaped_word}': {idx},\n")
            except Exception as e:
                print(f"Skipping problematic word with index {idx}: {e}")
        
        f.write("}\n\n")
        
        # Save Naive Bayes parameters
        f.write("# Naive Bayes parameters\n")
        f.write("nb_params = {\n")
        f.write(f" 'class_count': {nb_model.class_count_.tolist()},\n")
        f.write(f" 'class_log_prior': {nb_model.class_log_prior_.tolist()},\n")
        f.write(f" 'classes': {nb_model.classes_.tolist()},\n")
        f.write(f" 'feature_count': {nb_model.feature_count_.tolist()},\n")
        f.write(f" 'feature_log_prob': {nb_model.feature_log_prob_.tolist()}\n")
        f.write("}\n")
    
    print(f"Model parameters saved to {file_path}")

if __name__ == "__main__":
    train_and_save_model(r"C:\Users\Administrator\Downloads\spam.csv")
