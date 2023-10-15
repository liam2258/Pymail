import pytest
from unittest.mock import patch, Mock
from main import app

# Make a fake server that can be used for tests
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('main.psycopg.connect')
def test_send_email_success(mock_connect, client):
    # Create a mock connection and cursor
    mock_cursor = mock_connect.return_value.cursor.return_value

    # Define mock data
    mock_data = {
        "Name": "John Doe",
        "Contact": "johndoe@example.com",
        "Subject": "Test Subject",
        "Message": "Test Message"
    }

    # Make a POST request with the mock data
    response = client.post('/send', json=mock_data)

    # Assertions
    assert response.status_code == 200
    assert "message" in response.get_json() and response.get_json()["message"] == "Email sent"

    # Ensure the mock database was called with the correct query
    mock_cursor.execute.assert_called_once_with("INSERT INTO users (name, email) VALUES (%s, %s)",
                                               ("John Doe", "johndoe@example.com"))
# Create mock db and smtp connections
@patch('main.psycopg.connect')
@patch('main.smtplib.SMTP')
def test_send_email_failure(mock_smtp, mock_connect, client):
    # Create a mock connection and cursor
    mock_cursor = mock_connect.return_value.cursor.return_value

    # Mock the SMTP server
    mock_smtp_instance = Mock()
    mock_smtp.return_value = mock_smtp_instance
    mock_smtp_instance.sendmail.side_effect = Exception("SMTP error")

    # Define mock data with missing values
    mock_data = {
        "Name": "John Doe",
        "Contact": "johndoe@example.com",
        "Subject": "Test Subject",
        "Message": "Test Message"
    }

    # Make a POST request with the mock data
    response = client.post('/send', json=mock_data)

    # Assert the correct status code and error messages
    assert response.status_code == 500
    assert "error" in response.get_json() and response.get_json()["error"] == "Email not sent"
    assert "details" in response.get_json() and response.get_json()["details"] == "SMTP error"


    # Check if the database was called with the correct query
    mock_cursor.execute.assert_called_once_with("INSERT INTO users (name, email) VALUES (%s, %s)",
                                               ("John Doe", "johndoe@example.com"))

    # Ensure the mock smtp server was called
    assert mock_smtp_instance.sendmail.called

@patch('main.psycopg.connect')
def test_send_email_invalid_data(mock_connect, client):
    # Create a mock connection and cursor
    mock_cursor = mock_connect.return_value.cursor.return_value

    # Define invalid mock data
    mock_data = {
        "Name": "John Doe",
        "Contact": "johndoe@example.com"
        # Missing "Subject" and "Message"
    }

    # Make a POST request with the invalid mock data
    response = client.post('/send', json=mock_data)

    # Assert correct status code and error message
    assert response.status_code == 400
    assert "error" in response.get_json() and response.get_json()["error"] == "Incomplete JSON data"

    # Ensure the mock database was not called
    mock_cursor.execute.assert_not_called()

if __name__ == '__main__':
    pytest.main()
