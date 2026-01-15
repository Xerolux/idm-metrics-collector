import logging
import subprocess
from typing import Iterable, List

from .config import config

logger = logging.getLogger(__name__)


def _normalize_recipients(value) -> List[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [entry.strip() for entry in value.split(",") if entry.strip()]
    if isinstance(value, Iterable):
        return [str(entry).strip() for entry in value if str(entry).strip()]
    return []


def send_signal_message(message: str) -> None:
    if not config.get("signal.enabled", False):
        raise RuntimeError("Signal-Benachrichtigungen sind deaktiviert.")

    cli_path = config.get("signal.cli_path", "signal-cli")
    sender = config.get("signal.sender", "")
    recipients = _normalize_recipients(config.get("signal.recipients", []))

    if not sender:
        raise RuntimeError("Signal-Sender ist nicht konfiguriert.")
    if not recipients:
        raise RuntimeError("Keine Signal-Empfänger konfiguriert.")

    command = [cli_path, "-u", sender, "send", "-m", message] + recipients
    logger.info(f"Sending Signal message to {', '.join(recipients)}")
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Signal CLI Fehler")
