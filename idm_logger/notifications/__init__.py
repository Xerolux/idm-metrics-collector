# Xerolux 2026
# SPDX-License-Identifier: MIT
import logging
from typing import List
from .base import NotificationProvider
from .signal import SignalProvider
from .telegram import TelegramProvider
from .discord import DiscordProvider
from .email import EmailProvider

logger = logging.getLogger(__name__)


class NotificationManager:
    def __init__(self):
        self.providers: List[NotificationProvider] = [
            SignalProvider(),
            TelegramProvider(),
            DiscordProvider(),
            EmailProvider(),
        ]

    def send_all(self, message: str, **kwargs):
        """Send message via all enabled providers."""
        for provider in self.providers:
            # We catch exceptions here to ensure one failure doesn't stop others
            try:
                provider.send(message, **kwargs)
            except Exception as e:
                # Log unexpected exceptions that weren't caught by providers
                logger.error(
                    f"Unexpected error in {provider.name} provider: {e}", exc_info=True
                )


notification_manager = NotificationManager()
