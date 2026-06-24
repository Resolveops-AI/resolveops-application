import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("api.get_users_table")
@patch("notifications.send_otp_email")
def test_request_otp_new_user(mock_send_email, mock_get_table):
    # Mock DynamoDB table response
    mock_table = MagicMock()
    mock_table.get_item.return_value = {}  # User not found
    mock_get_table.return_value = mock_table
    
    mock_send_email.return_value = True
    
    response = client.post("/api/request-otp", json={
        "email": "test@example.com",
        "full_name": "Test User"
    })
    
    assert response.status_code == 200
    assert "OTP sent" in response.json()["message"]

@patch("api.get_users_table")
def test_request_otp_existing_user(mock_get_table):
    mock_table = MagicMock()
    mock_table.get_item.return_value = {"Item": {"email": "test@example.com"}}
    mock_get_table.return_value = mock_table
    
    response = client.post("/api/request-otp", json={
        "email": "test@example.com",
        "full_name": "Test User"
    })
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@patch("api.get_users_table")
def test_login_invalid_user(mock_get_table):
    mock_table = MagicMock()
    mock_table.get_item.return_value = {}  # User not found
    mock_get_table.return_value = mock_table
    
    response = client.post("/api/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401

def test_chat_without_auth():
    response = client.post("/api/chat", json={"message": "hello"})
    # Should be rejected because no JWT is provided
    assert response.status_code == 401

def test_get_keys_without_auth():
    response = client.get("/api/keys")
    assert response.status_code == 401
