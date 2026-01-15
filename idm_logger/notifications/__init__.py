from typing import List
from .base import NotificationProvider
from .signal import SignalProvider
from .telegram import TelegramProvider
from .discord import DiscordProvider
from .email import EmailProvider

class NotificationManager:
    def __init__(self):
        self.providers: List[NotificationProvider] = [
            SignalProvider(),
            TelegramProvider(),
            DiscordProvider(),
            EmailProvider()
        ]

    def send_all(self, message: str, **kwargs):
        """Send message via all enabled providers."""
        for provider in self.providers:
            # We catch exceptions here to ensure one failure doesn't stop others
            try:
                provider.send(message, **kwargs)
            except Exception:
                # Logged inside providers usually, but just in case
                pass

notification_manager = NotificationManager()
