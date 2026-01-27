# SPDX-License-Identifier: MIT
"""Tests for variable functionality."""

import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import helper from conftest
from conftest import create_mock_db_module, create_mock_config


class TestVariables(unittest.TestCase):
    def setUp(self):
        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

        # Create properly configured mocks
        self.mock_db_module = create_mock_db_module()
        self.mock_config = create_mock_config()

        # Configure config for variables
        self.mock_config.data["variables"] = []

        # Mock modules
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "idm_logger.db": self.mock_db_module,
                "idm_logger.mqtt": MagicMock(),
                "idm_logger.scheduler": MagicMock(),
                "idm_logger.modbus": MagicMock(),
            },
        )
        self.modules_patcher.start()

        # Patch config instance
        self.config_patcher = patch("idm_logger.config.config", self.mock_config)
        self.config_patcher.start()

        # Import web and variable manager
        import idm_logger.web as web
        from idm_logger.variables import VariableManager

        self.web = web
        self.app = web.app
        self.app.config["TESTING"] = True
        self.app.secret_key = b"test-secret"
        self.client = self.app.test_client()

        # Re-initialize variable manager
        self.variable_manager = VariableManager(self.mock_config)
        self.web.variable_manager = self.variable_manager

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

    def test_manager_add_variable(self):
        var = self.variable_manager.add_variable(
            var_id="hp_id",
            name="Heatpump",
            var_type="query",
            query="label_values(idm_heatpump_status, heatpump_id)",
            default="1",
        )

        self.assertEqual(var.id, "hp_id")
        self.assertEqual(var.name, "Heatpump")
        self.assertEqual(var.type, "query")

        # Check config
        self.assertEqual(len(self.mock_config.data["variables"]), 1)
        self.assertEqual(self.mock_config.data["variables"][0]["id"], "hp_id")
        self.mock_config.save.assert_called()

    def test_manager_get_variable(self):
        self.mock_config.data["variables"] = [
            {"id": "v1", "name": "V1", "type": "custom", "values": ["A", "B"]}
        ]

        var = self.variable_manager.get_variable("v1")
        self.assertIsNotNone(var)
        self.assertEqual(var.name, "V1")
        self.assertEqual(var.values, ["A", "B"])

    def test_manager_update_variable(self):
        self.mock_config.data["variables"] = [
            {"id": "v1", "name": "Old", "type": "custom"}
        ]

        updated = self.variable_manager.update_variable("v1", name="New")
        self.assertEqual(updated.name, "New")
        self.assertEqual(self.mock_config.data["variables"][0]["name"], "New")

    def test_manager_delete_variable(self):
        self.mock_config.data["variables"] = [
            {"id": "v1", "name": "Delete me", "type": "custom"}
        ]

        success = self.variable_manager.delete_variable("v1")
        self.assertTrue(success)
        self.assertEqual(len(self.mock_config.data["variables"]), 0)

    def test_substitute_variables_bracket_syntax(self):
        query = "rate(metric{id='{id}'}[5m])"
        values = {"id": "123"}
        result = self.variable_manager.substitute_variables(query, values)
        self.assertEqual(result, "rate(metric{id='123'}[5m])")

    def test_substitute_variables_dollar_syntax(self):
        query = "rate(metric{id='$id'}[5m])"
        values = {"id": "123"}
        result = self.variable_manager.substitute_variables(query, values)
        self.assertEqual(result, "rate(metric{id='123'}[5m])")

    def test_substitute_variables_dollar_brace_syntax(self):
        query = "rate(metric{id='${id}'}[5m])"
        values = {"id": "123"}
        result = self.variable_manager.substitute_variables(query, values)
        self.assertEqual(result, "rate(metric{id='123'}[5m])")

    def test_substitute_variables_mixed(self):
        query = "metric_$unit{host='{host}'}"
        values = {"unit": "temp", "host": "localhost"}
        result = self.variable_manager.substitute_variables(query, values)
        self.assertEqual(result, "metric_temp{host='localhost'}")

    def test_api_create_variable(self):
        payload = {
            "id": "v1",
            "name": "Var 1",
            "type": "custom",
            "values": ["1", "2"],
            "default": "1",
        }

        response = self.client.post(
            "/api/variables", data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["id"], "v1")
        self.assertEqual(len(self.mock_config.data["variables"]), 1)

    def test_api_substitute(self):
        payload = {"query": "test_$var", "variables": {"var": "success"}}

        response = self.client.post(
            "/api/variables/substitute",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["result"], "test_success")


if __name__ == "__main__":
    unittest.main()
