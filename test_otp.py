import requests

url = "https://resolveops-ai.sathvikdevops.online/api/request-otp"
data = {"email": "test@example.com", "full_name": "Test User"}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
