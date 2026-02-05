#!/usr/bin/env python3
"""
Xerolux 2026 - Lokaler Admin-Test mit deiner Installation ID

Testet ob deine lokale Installation als Admin erkannt wird.
"""

import os
import json


# Prüfe lokale installation_id
def check_local_installation_id():
    """Liest die lokale installation_id aus der Datenbank"""
    print("=" * 60)
    print("PRÜFE LOKALE INSTALLATION ID")
    print("=" * 60)

    # Suche nach Datenbank
    db_path = None
    # Search in parent directory since script is in scripts/
    search_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for root, dirs, files in os.walk(search_dir):
        if "settings.db" in files or "idm_logger.db" in files:
            db_path = os.path.join(
                root, files[0] if "settings.db" in files else "idm_logger.db"
            )
            break

    if not db_path:
        print("[WARNUNG] Keine Datenbank gefunden")
        print("Erstelle Test mit deiner Admin-ID aus .env")
        return "075e0c34-f67f-4882-9637-90ea85971a79"

    print(f"[OK] Datenbank gefunden: {db_path}")

    # Versuche die ID zu lesen
    try:
        import sqlite3

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Lese config
        cursor.execute("SELECT value FROM settings WHERE key = 'config'")
        row = cursor.fetchone()

        if row:
            config = json.loads(row[0])
            installation_id = config.get("installation_id")
            print(f"\n[OK] Installation ID: {installation_id}")
            conn.close()
            return installation_id
        else:
            print("[WARNUNG] Keine Config in Datenbank gefunden")
            conn.close()
            return "075e0c34-f67f-4882-9637-90ea85971a79"

    except Exception as e:
        print(f"[ERROR] Konnte ID nicht lesen: {e}")
        return "075e0c34-f67f-4882-9637-90ea85971a79"


def test_local_server(installation_id):
    """Testet den lokalen Server mit der Admin-ID"""
    print("\n" + "=" * 60)
    print("TESTE LOKALEN SERVER")
    print("=" * 60)

    admin_id = "075e0c34-f67f-4882-9637-90ea85971a79"

    print(f"\nDeine Admin-ID aus .env: {admin_id}")
    print(f"Deine lokale Installation ID: {installation_id}")

    if installation_id.lower() == admin_id.lower():
        print("\n[INFO] Deine Installation ID IST die Admin-ID!")
        print("[INFO] Du solltest Admin-Rechte erhalten.")
    else:
        print("\n[WARNUNG] IDs stimmen nicht überein!")
        print("[INFO] Damit du Admin-Rechte bekommst, müsste deine Installation ID")
        print(f"       die Admin-ID sein: {admin_id}")

    # Teste Server-Endpoint lokal
    print("\n" + "-" * 60)
    print("Teste /api/v1/model/check Endpunkt:")
    print("-" * 60)

    try:
        import requests

        # Lokaler Server (wenn er läuft)
        local_url = "http://localhost:5000/api/v1/model/check"
        params = {"installation_id": admin_id}

        print(f"\n[Sende] GET {local_url}")
        print(f"[Parameter] installation_id={admin_id}")

        response = requests.get(local_url, params=params, timeout=5)

        print(f"\n[Antwort] Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"[Antwort] is_admin: {data.get('is_admin', False)}")

            if data.get("is_admin"):
                print("\n[ERFOLG] Admin-Zugang funktioniert!")
                if "server_stats" in data:
                    stats = data["server_stats"]
                    print("\nServer Statistiken:")
                    print(f"  - Modelle: {len(stats.get('models', []))}")
                    print(
                        f"  - Aktive Installationen: {stats.get('active_installations', 0)}"
                    )
                    print(f"  - Gesamte Datenpunkte: {stats.get('total_points', 0)}")
            else:
                print("\n[INFO] Kein Admin-Zugang (normale Installation)")
        else:
            print(f"[ERROR] Server antwortet mit Status {response.status_code}")
            print(f"[ERROR] {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n[WARNUNG] Lokaler Server läuft nicht auf localhost:5000")
        print("[INFO] Um zu testen, starte den Server mit:")
        print("       docker compose up -d")
        print("   oder:")
        print("       cd telemetry_server && python -m uvicorn app:app --reload")

    except Exception as e:
        print(f"\n[ERROR] Test fehlgeschlagen: {e}")


def show_how_to_configure():
    """Zeigt wie man die Admin-ID konfiguriert"""
    print("\n" + "=" * 60)
    print("WIE DU ADMIN-RECHTE BEKOMMST")
    print("=" * 60)

    print("\nOption 1: Deine Installation ID auf Admin-ID setzen")
    print("-" * 60)
    print("Wenn du möchten, dass deine lokale Installation Admin-Rechte hat,")
    print("musst du die installation_id in der Datenbank auf die Admin-ID setzen.")
    print("\nSQL Befehl (in der Datenbank):")
    print(
        "  UPDATE settings SET value = json_set(value, '$.installation_id', '075e0c34-f67f-4882-9637-90ea85971a79')"
    )
    print("  WHERE key = 'config';")

    print("\nOption 2: Deine ID zur Admin-Liste hinzufügen")
    print("-" * 60)
    print("Oder füge deine aktuelle ID zur .env Datei hinzu:")
    print(
        "  ADMIN_INSTALLATION_IDS=075e0c34-f67f-4882-9637-90ea85971a79,<deine-id-hier>"
    )


if __name__ == "__main__":
    installation_id = check_local_installation_id()
    test_local_server(installation_id)
    show_how_to_configure()
