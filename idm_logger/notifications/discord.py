import logging
import requests
from .base import NotificationProvider
from ..config import config

logger = logging.getLogger(__name__)

class DiscordProvider(NotificationProvider):
    @property
    def name(self) -> str:
        return "discord"

    def send(self, message: str, **kwargs) -> bool:
        if not config.get("discord.enabled", False):
            return False

        webhook_url = config.get("discord.webhook_url")

        if not webhook_url:
            logger.error("Discord webhook_url not configured")
            return False

        try:
            response = requests.post(webhook_url, json={
                "content": message
            }, timeout=10)
            if not response.ok:
                 logger.error(f"Discord Webhook error: {response.text}")
                 return False
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord message: {e}")
            return False
