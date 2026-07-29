# Xerolux 2026
# SPDX-License-Identifier: MIT
import json
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from idm_logger import web


def _authenticated_client():
    web.app.config["TESTING"] = True
    client = web.app.test_client()
    with client.session_transaction() as session:
        session["logged_in"] = True
    return client


@patch("idm_logger.web.requests.get")
def test_database_export_streams_all_series_as_valid_json(mock_get):
    upstream = MagicMock(status_code=200)
    upstream.iter_lines.return_value = iter(
        [
            b'{"metric":{"__name__":"idm_heatpump_temp","unit":"c"},"values":[21.5],"timestamps":[1000]}',
            b'{"metric":{"__name__":"custom_metric"},"values":[7],"timestamps":[2000]}',
        ]
    )
    mock_get.return_value = upstream

    response = _authenticated_client().get("/api/export/database")
    payload = json.loads(response.data)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert "attachment" in response.headers["Content-Disposition"]
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Accel-Buffering"] == "no"
    assert [item["metric"]["__name__"] for item in payload["series"]] == [
        "idm_heatpump_temp",
        "custom_metric",
    ]
    assert payload["export_info"]["scope"] == "all"
    mock_get.assert_called_once()
    assert mock_get.call_args.kwargs["params"]["match[]"] == '{__name__=~".+"}'
    assert mock_get.call_args.kwargs["timeout"] == (10, None)
    upstream.close.assert_called_once()


def test_database_export_requires_login():
    web.app.config["TESTING"] = True
    response = web.app.test_client().post("/api/export/database")
    assert response.status_code == 401
