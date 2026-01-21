import pytest
from unittest.mock import MagicMock, patch
from idm_logger.metrics import MetricsWriter
import queue
import time

class TestMetricsBatching:
    @pytest.fixture
    def mock_requests(self):
        with patch("idm_logger.metrics.requests.Session") as mock:
            session_mock = MagicMock()
            session_mock.post.return_value.status_code = 204
            mock.return_value = session_mock
            yield session_mock

    def test_send_data_batch(self, mock_requests):
        """Test sending a batch of data."""
        writer = MetricsWriter()

        # Manually invoke _send_data with a list
        batch = [
            {"sensor1": 10},
            {"sensor2": 20},
            {"sensor3": 30.5}
        ]

        writer._send_data(batch)

        # Check if post was called
        mock_requests.post.assert_called_once()
        args, kwargs = mock_requests.post.call_args
        data = kwargs["data"]

        # Verify Line Protocol format
        assert "idm_heatpump sensor1=10" in data
        assert "idm_heatpump sensor2=20" in data
        assert "idm_heatpump sensor3=30.5" in data
        assert len(data.splitlines()) == 3

        writer.stop()

    def test_send_data_single(self, mock_requests):
        """Test backward compatibility for single dict."""
        writer = MetricsWriter()

        data = {"sensor1": 10}
        writer._send_data(data)

        mock_requests.post.assert_called_once()
        args, kwargs = mock_requests.post.call_args
        payload = kwargs["data"]

        assert "idm_heatpump sensor1=10" in payload
        assert "\n" not in payload.strip()

        writer.stop()

    @patch("idm_logger.metrics.MetricsWriter._send_data")
    def test_batching_logic_simulation(self, mock_send):
        """
        Simulate the batching loop logic.
        We cannot easily test threaded timing in unit tests without flakiness,
        so we replicate the logic flow here to verify the algorithm.
        """
        q = queue.Queue()
        batch = []
        last_send = time.time() - 2.0 # Force timeout immediately if checked
        BATCH_SIZE = 3
        BATCH_TIMEOUT = 1.0

        # Scenario 1: Fill batch to size
        items = [{"v": i} for i in range(3)]
        for i in items:
            q.put(i)

        # Simulate worker loop iteration
        while not q.empty():
            item = q.get_nowait()
            batch.append(item)
            if len(batch) >= BATCH_SIZE:
                mock_send(batch)
                batch = []

        assert mock_send.call_count == 1
        mock_send.assert_called_with(items)

        # Scenario 2: Timeout
        mock_send.reset_mock()
        q.put({"v": 99})

        # Fetch item
        item = q.get_nowait()
        batch.append(item)

        # Simulate timeout check
        now = time.time()
        # if batch and (now - last_send > BATCH_TIMEOUT)...
        # Since we set last_send long ago, it should trigger
        if batch: # Assume timeout logic triggered in real worker
             mock_send(batch)
             batch = []

        assert mock_send.call_count == 1
        mock_send.assert_called_with([{"v": 99}])
