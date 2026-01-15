
import pytest
from unittest.mock import patch, MagicMock
from idm_logger.web import app
import time

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['logged_in'] = True
        yield client

def test_technician_code_returns_server_time(client):
    # Mock calculate_codes to return dummy codes
    with patch('idm_logger.web.calculate_codes') as mock_calc:
        mock_calc.return_value = {"level_1": "1234", "level_2": "12345"}

        response = client.get('/api/tools/technician-code')

        assert response.status_code == 200
        data = response.get_json()
        assert "server_time" in data
        # Check format HH:MM:SS
        assert len(data["server_time"].split(":")) == 3
        assert data["level_1"] == "1234"
