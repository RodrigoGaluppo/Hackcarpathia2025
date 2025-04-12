import requests
import json
import sys

def test_predict_endpoint():
    url = "http://localhost:5328/api/predict"
    
    # Test data
    test_data = {
        "messages": [
            "Your account has been compromised. Click here to reset your password.",
            "Congratulations! You've won a free trip to the Bahamas!",
            "Hi Jane, can we meet at 3 PM tomorrow?"
        ]
    }
    
    print("Sending request to", url)
    print("Test data:", json.dumps(test_data, indent=2))
    
    try:
        # Send POST request
        response = requests.post(url, json=test_data, timeout=10)
        
        # Print results
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the server. Is it running?")
    except requests.exceptions.Timeout:
        print("Timeout error: The server took too long to respond.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    print("Starting API test...")
    test_predict_endpoint()
    print("Test completed.")