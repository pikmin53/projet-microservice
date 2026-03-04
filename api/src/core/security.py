import requests
import os

AUTH_URL = os.getenv("API_AUTH_URL")
def verify_token(request):
    try:
        response = requests.get(f"{AUTH_URL}/verifyToken", headers=request.headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error verifying token: {e}")
    return None
