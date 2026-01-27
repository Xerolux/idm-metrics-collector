import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestAnnotations(unittest.TestCase):
    def setUp(self):
        # Ensure cryptography is loaded

        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

        # Mock modules
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "idm_logger.db": MagicMock(),
                "idm_logger.mqtt": MagicMock(),
                "idm_logger.scheduler": MagicMock(),
                "idm_logger.modbus": MagicMock(),
                "pandas": MagicMock(),
                "numpy": MagicMock(),
            },
        )
        self.modules_patcher.start()

        # Import config with json.loads patched
        with patch("json.loads", return_value={}):
            pass

        # Patch config instance
        self.config_patcher = patch("idm_logger.config.config")
        self.mock_config = self.config_patcher.start()

        # Configure config
        self.mock_config.get_flask_secret_key.return_value = "secret"
        self.mock_config.get.return_value = None
        self.mock_config.data = {"annotations": []}

        # Mock save method
        self.mock_config.save = MagicMock()

        # Import web and annotation manager
        import idm_logger.web as web
        from idm_logger.annotations import AnnotationManager

        self.web = web
        self.app = web.app
        self.client = self.app.test_client()

        # Re-initialize annotation manager with mocked config
        self.annotation_manager = AnnotationManager(self.mock_config)
        self.web.annotation_manager = self.annotation_manager

        # Set session for login_required
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

    def tearDown(self):
        self.config_patcher.stop()
        self.modules_patcher.stop()
        # Clean up modules again to prevent pollution
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

    def test_manager_add_annotation(self):
        ann = self.annotation_manager.add_annotation(
            time=1234567890,
            text="Test Annotation",
            tags=["tag1", "tag2"],
            color="#000000",
            dashboard_id="dash1",
        )

        self.assertEqual(ann.time, 1234567890)
        self.assertEqual(ann.text, "Test Annotation")
        self.assertEqual(ann.tags, ["tag1", "tag2"])
        self.assertEqual(ann.dashboard_id, "dash1")

        # Check if saved to config
        self.assertEqual(len(self.mock_config.data["annotations"]), 1)
        self.assertEqual(self.mock_config.data["annotations"][0]["id"], ann.id)
        self.mock_config.save.assert_called()

    def test_manager_get_annotations(self):
        # Add some dummy data
        self.mock_config.data["annotations"] = [
            {"id": "1", "time": 100, "text": "A1", "dashboard_id": "d1"},
            {"id": "2", "time": 200, "text": "A2", "dashboard_id": "d2"},
            {"id": "3", "time": 300, "text": "A3", "dashboard_id": None},  # Global
        ]

        # Test get all
        all_anns = self.annotation_manager.get_all_annotations()
        self.assertEqual(len(all_anns), 3)

        # Test filter by dashboard
        d1_anns = self.annotation_manager.get_annotations_for_dashboard("d1")
        self.assertEqual(len(d1_anns), 2)  # A1 + A3 (global)
        ids = [a.id for a in d1_anns]
        self.assertIn("1", ids)
        self.assertIn("3", ids)

        # Test filter by time
        range_anns = self.annotation_manager.get_annotations_for_time_range(150, 250)
        self.assertEqual(len(range_anns), 1)
        self.assertEqual(range_anns[0].id, "2")

    def test_manager_update_annotation(self):
        self.mock_config.data["annotations"] = [
            {"id": "1", "time": 100, "text": "Old", "tags": []}
        ]

        updated = self.annotation_manager.update_annotation(
            "1", text="New", tags=["updated"]
        )

        self.assertEqual(updated.text, "New")
        self.assertEqual(updated.tags, ["updated"])
        self.assertEqual(self.mock_config.data["annotations"][0]["text"], "New")
        self.mock_config.save.assert_called()

        # Test non-existent
        result = self.annotation_manager.update_annotation("999", text="Fail")
        self.assertIsNone(result)

    def test_manager_delete_annotation(self):
        self.mock_config.data["annotations"] = [
            {"id": "1", "time": 100, "text": "Delete me"}
        ]

        success = self.annotation_manager.delete_annotation("1")
        self.assertTrue(success)
        self.assertEqual(len(self.mock_config.data["annotations"]), 0)
        self.mock_config.save.assert_called()

        # Delete again
        success = self.annotation_manager.delete_annotation("1")
        self.assertFalse(success)

    def test_api_create_annotation(self):
        payload = {
            "time": 1000,
            "text": "API Test",
            "tags": ["api"],
            "color": "#fff",
            "dashboard_id": "d1",
        }

        response = self.client.post(
            "/api/annotations",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["text"], "API Test")
        self.assertEqual(len(self.mock_config.data["annotations"]), 1)

    def test_api_get_annotations(self):
        self.mock_config.data["annotations"] = [
            {"id": "1", "time": 100, "text": "A1", "dashboard_id": "d1"}
        ]

        response = self.client.get("/api/annotations")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "1")

    def test_api_get_annotations_filtered(self):
        self.mock_config.data["annotations"] = [
            {"id": "1", "time": 100, "text": "A1", "dashboard_id": "d1"},
            {"id": "2", "time": 200, "text": "A2", "dashboard_id": "d2"},
        ]

        response = self.client.get("/api/annotations?dashboard_id=d1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "1")

    def test_api_update_annotation(self):
        self.mock_config.data["annotations"] = [{"id": "1", "time": 100, "text": "Old"}]

        response = self.client.put(
            "/api/annotations/1",
            data=json.dumps({"text": "New"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.mock_config.data["annotations"][0]["text"], "New")

    def test_api_delete_annotation(self):
        self.mock_config.data["annotations"] = [
            {"id": "1", "time": 100, "text": "Delete me"}
        ]

        response = self.client.delete("/api/annotations/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.mock_config.data["annotations"]), 0)


if __name__ == "__main__":
    unittest.main()
