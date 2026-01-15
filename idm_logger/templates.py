"""
Predefined templates for alerts.
"""

ALERT_TEMPLATES = [
    {
        "name": "Störung an der Wärmepumpe",
        "description": "Alarm bei allgemeiner Störung (Summenstörung)",
        "alert_data": {
            "name": "Wärmepumpe Störung",
            "type": "threshold",
            "sensor": "Summenstörung Wärmepumpe",
            "condition": "=",
            "threshold": "1",
            "message": "ACHTUNG: Störung an der Wärmepumpe erkannt! ({time})",
            "interval_seconds": 3600,
        },
    },
    {
        "name": "Warmwasser kalt",
        "description": "Alarm wenn Warmwasser unter 40°C fällt",
        "alert_data": {
            "name": "Warmwasser Kalt",
            "type": "threshold",
            "sensor": "Warmwasserzapftemperatur (B42)",
            "condition": "<",
            "threshold": "40",
            "message": "Warmwasser ist kalt: {value}°C um {time}",
            "interval_seconds": 7200,
        },
    },
    {
        "name": "Hohe Vorlauftemperatur",
        "description": "Alarm wenn Vorlauf über 60°C steigt",
        "alert_data": {
            "name": "Vorlauf Hoch",
            "type": "threshold",
            "sensor": "Wärmepumpen Vorlauftemperatur (B33)",
            "condition": ">",
            "threshold": "60",
            "message": "Warnung: Vorlauf sehr hoch ({value}°C)!",
            "interval_seconds": 3600,
        },
    },
    {
        "name": "Täglicher Statusbericht",
        "description": "Sendet einmal täglich einen Statusbericht",
        "alert_data": {
            "name": "Tagesbericht",
            "type": "status",
            "message": "Statusbericht {time}: System läuft.",
            "interval_seconds": 86400,
        },
    },
    {
        "name": "Smart Grid: EVU Sperre",
        "description": "Info wenn EVU Sperre aktiv ist",
        "alert_data": {
            "name": "EVU Sperre",
            "type": "threshold",
            "sensor": "EVU - Sperrkontakt",
            "condition": "=",
            "threshold": "0",
            "message": "Info: EVU Sperre ist aktiv um {time}",
            "interval_seconds": 3600,
        },
    },
]


def get_alert_templates():
    return ALERT_TEMPLATES
