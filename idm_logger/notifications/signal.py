import logging
import subprocess
from typing import Iterable, List
from shutil import which
from .base import NotificationProvider
from ..config import config

logger = logging.getLogger(__name__)

class SignalProvider(NotificationProvider):
    @property
    def name(self) -> str:
        return "signal"

    def _normalize_recipients(self, value) -> List[str]:
        if not value:
            return []
        if isinstance(value, str):
            return [entry.strip() for entry in value.split(',') if entry.strip()]
        if isinstance(value, Iterable):
            return [str(entry).strip() for entry in value if str(entry).strip()]
        return []

    def send(self, message: str, **kwargs) -> bool:
        if not config.get("signal.enabled", False):
            return False

        cli_path = config.get("signal.cli_path", "signal-cli")
        if not which(cli_path):
             logger.error(f"Signal CLI not found at {cli_path}")
             return False

        sender = config.get("signal.sender", "")
        recipients = self._normalize_recipients(config.get("signal.recipients", []))

        if not sender or not recipients:
             logger.error("Signal sender or recipients not configured")
             return False

        try:
            command = [cli_path, "-u", sender, "send", "-m", message] + recipients
            logger.debug(f"Sending Signal message to {', '.join(recipients)}")
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.error(f"Signal CLI error: {result.stderr.strip()}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to send Signal message: {e}")
            return False
