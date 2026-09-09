# Xerolux 2026
# SPDX-License-Identifier: MIT
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class NotificationProvider(ABC):
    """Abstract base class for notification providers."""

    @abstractmethod
    def send(self, message: str, **kwargs) -> bool:
        """Send a message."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass
