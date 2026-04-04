# Xerolux 2026
# SPDX-License-Identifier: MIT
import logging
import re
import subprocess
import shutil
import os
from typing import Iterable, List

from .config import config

logger = logging.getLogger(__name__)

# Valid phone number pattern (international format: +country code + number)
_PHONE_PATTERN = re.compile(r"^\+[1-9]\d{6,14}$")

# Maximum message length to prevent DoS
_MAX_MESSAGE_LENGTH = 1000

# Dangerous characters that should not be in messages (prevents injection)
# Allow: alphanumeric, basic punctuation, spaces, newlines, German umlauts
_SAFE_MESSAGE_PATTERN = re.compile(
    r"^[\w\s\.\,\!\?\:\;\-\+\(\)\[\]\{\}\/\@\#\&\%\$\=\ä\ö\ü\Ä\Ö\Ü\ß\n\r]+$"
)


def _resolve_signal_cli(cli_path: str) -> str:
    """Resolve signal-cli to a safe executable path."""
    normalized = (cli_path or "signal-cli").strip()
    if not re.match(r"^[a-zA-Z0-9_\-/\.]+$", normalized):
        raise RuntimeError("Signal CLI Pfad enthält ungültige Zeichen.")

    if os.path.sep in normalized:
        abs_path = os.path.abspath(normalized)
        if not os.path.isabs(abs_path):
            raise RuntimeError("Signal CLI Pfad muss absolut sein.")
        if os.path.basename(abs_path) != "signal-cli":
            raise RuntimeError("Nur 'signal-cli' ist als Executable erlaubt.")
        if not os.path.isfile(abs_path):
            raise RuntimeError(f"Signal CLI Executable nicht gefunden: {abs_path}")
        if not os.access(abs_path, os.X_OK):
            raise RuntimeError(f"Signal CLI Executable nicht ausführbar: {abs_path}")
        return abs_path

    if normalized != "signal-cli":
        raise RuntimeError("Nur der Befehl 'signal-cli' ist erlaubt.")
    resolved = shutil.which("signal-cli")
    if not resolved:
        raise RuntimeError("Signal CLI Befehl 'signal-cli' nicht im PATH gefunden.")
    return resolved


def _validate_phone_number(number: str) -> bool:
    """Validate that a string looks like a valid international phone number."""
    return bool(_PHONE_PATTERN.match(number))


def _normalize_recipients(value) -> List[str]:
    if not value:
        return []
    if isinstance(value, str):
        entries = [entry.strip() for entry in value.split(",") if entry.strip()]
    elif isinstance(value, Iterable):
        entries = [str(entry).strip() for entry in value if str(entry).strip()]
    else:
        return []

    # Validate and filter recipients
    valid_recipients = []
    for entry in entries:
        if _validate_phone_number(entry):
            valid_recipients.append(entry)
        else:
            logger.warning(
                f"Invalid Signal recipient format (skipped): {entry[:20]}..."
            )

    return valid_recipients


def _validate_message(message: str) -> str:
    """Validate and sanitize message to prevent command injection."""
    if not isinstance(message, str):
        raise RuntimeError("Signal Nachricht muss ein String sein.")

    # Check length
    if len(message) > _MAX_MESSAGE_LENGTH:
        raise RuntimeError(
            f"Signal Nachricht zu lang (max {_MAX_MESSAGE_LENGTH} Zeichen)."
        )

    # Check for null bytes
    if "\x00" in message:
        raise RuntimeError("Signal Nachricht enthält ungültige Zeichen.")

    if not _SAFE_MESSAGE_PATTERN.match(message):
        raise RuntimeError("Signal Nachricht enthält nicht erlaubte Zeichen.")

    # Trim leading/trailing whitespace but preserve internal formatting
    return message.strip()


def send_signal_message(message: str) -> None:
    if not config.get("signal.enabled", False):
        raise RuntimeError("Signal-Benachrichtigungen sind deaktiviert.")

    # Validate and sanitize message FIRST
    message = _validate_message(message)

    # Always use signal-cli from PATH to avoid command path injection.
    cli_path = "signal-cli"
    sender = config.get("signal.sender", "")

    # Validate sender
    if not sender:
        raise RuntimeError("Signal-Sender ist nicht konfiguriert.")
    if not _validate_phone_number(sender):
        raise RuntimeError("Signal-Sender hat ungültiges Format (erwartet: +49...).")

    recipients = _normalize_recipients(config.get("signal.recipients", []))
    if not recipients:
        raise RuntimeError("Keine gültigen Signal-Empfänger konfiguriert.")

    cli_executable = _resolve_signal_cli(cli_path)
    command = [
        cli_executable,
        "-u",
        sender,
        "send",
        "--message-from-stdin",
    ] + recipients
    logger.info(f"Sending Signal message to {len(recipients)} recipient(s)")
    result = subprocess.run(
        command,
        input=message,
        capture_output=True,
        text=True,
        timeout=30,
        shell=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Signal CLI Fehler")
