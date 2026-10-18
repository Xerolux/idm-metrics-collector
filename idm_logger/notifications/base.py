# Xerolux 2026
# SPDX-License-Identifier: MIT
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class NotificationProvider(ABC):
    """Abstract base class for notification providers."""

    @abstractmethod
    def send(self, message: str, **kwargs) -> bool:
        """Send a message."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
