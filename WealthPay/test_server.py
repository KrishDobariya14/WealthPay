import requests
import json

def test_chatbox():
    try:
        # Test the chatbox endpoint
        url = "http://localhost:8000/api/chatbox/"
        data = {"user_input": "What is investment?"}
        
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Server is working correctly!")
        else:
            print("❌ Server returned an error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chatbox()
