import logging
import requests
from .base import NotificationProvider
from ..config import config

logger = logging.getLogger(__name__)

class TelegramProvider(NotificationProvider):
    @property
    def name(self) -> str:
        return "telegram"

    def send(self, message: str, **kwargs) -> bool:
        if not config.get("telegram.enabled", False):
            return False

        token = config.get("telegram.bot_token")
        chat_ids = config.get("telegram.chat_ids")

        if not token or not chat_ids:
            logger.error("Telegram token or chat_ids not configured")
            return False

        if isinstance(chat_ids, str):
            chat_ids = [x.strip() for x in chat_ids.split(",") if x.strip()]

        success = True
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        for chat_id in chat_ids:
            try:
                response = requests.post(url, json={
                    "chat_id": chat_id,
                    "text": message
                }, timeout=10)
                if not response.ok:
                    logger.error(f"Telegram API error for {chat_id}: {response.text}")
                    success = False
            except Exception as e:
                logger.error(f"Failed to send Telegram message: {e}")
                success = False

        return success
