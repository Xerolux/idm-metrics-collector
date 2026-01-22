
import sys
import os

# Add the project root to the path
sys.path.append(os.getcwd())

from idm_logger.dashboard_config import get_default_dashboards

def test_default_dashboards():
    dashboards = get_default_dashboards()

    assert len(dashboards) == 1
    dashboard = dashboards[0]
    assert dashboard['name'] == "Home Dashboard"

    charts = dashboard['charts']
    print(f"Found {len(charts)} charts in default dashboard")

    # Verify specific charts
    titles = [c['title'] for c in charts]
    expected_titles = [
        "Wärmepumpe Temperaturen",
        "Warmwasser Temperaturen",
        "Leistung",
        "Energie (kumuliert)",
        "Heizkreis A - Temperaturen",
        "Speicher & Quelltemperaturen",
        "COP Verlauf",
        "AI Anomalie-Erkennung"
    ]

    for title in expected_titles:
        assert title in titles, f"Missing chart: {title}"

    print("All expected charts found.")

    # Check chart structure
    for chart in charts:
        assert 'id' in chart
        assert 'queries' in chart
        assert 'hours' in chart
        assert len(chart['queries']) > 0

    print("Chart structure verification passed.")

if __name__ == "__main__":
    try:
        test_default_dashboards()
        print("Test passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
