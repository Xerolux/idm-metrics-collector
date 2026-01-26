# SPDX-License-Identifier: MIT
"""
Heat Pump Manufacturer Driver Registry.

This module provides a central registry for all supported heat pump
manufacturers and models. Drivers are automatically discovered and
registered at import time.

Usage:
    from idm_logger.manufacturers import ManufacturerRegistry

    # List all supported manufacturers
    manufacturers = ManufacturerRegistry.list_manufacturers()

    # Get a specific driver
    driver = ManufacturerRegistry.get_driver("idm", "navigator_2_0")
    if driver:
        sensors = driver.get_sensors(config)
        capabilities = driver.get_capabilities()
"""

from typing import Dict, List, Optional, Type
import logging

from .base import (
    HeatpumpDriver,
    SensorDefinition,
    SensorCategory,
    DataType,
    AccessMode,
    HeatpumpCapabilities,
    ConnectionConfig,
    ReadGroup,
)

logger = logging.getLogger(__name__)

# Re-export base classes
__all__ = [
    "ManufacturerRegistry",
    "HeatpumpDriver",
    "SensorDefinition",
    "SensorCategory",
    "DataType",
    "AccessMode",
    "HeatpumpCapabilities",
    "ConnectionConfig",
    "ReadGroup",
]


class ManufacturerRegistry:
    """
    Central registry for heat pump drivers.

    This class manages the registration and lookup of heat pump drivers
    for different manufacturers and models.
    """

    _drivers: Dict[str, Dict[str, Type[HeatpumpDriver]]] = {}
    _instances: Dict[str, HeatpumpDriver] = {}

    # Display names for manufacturers
    _manufacturer_names: Dict[str, str] = {
        "idm": "iDM Energiesysteme",
        "nibe": "NIBE",
        "daikin": "Daikin",
        "luxtronik": "Luxtronik (Bosch, Alpha Innotec, Novelan)",
        "viessmann": "Viessmann",
        "vaillant": "Vaillant",
        "stiebel_eltron": "Stiebel Eltron",
        "ochsner": "Ochsner",
        "waterkotte": "Waterkotte",
    }

    @classmethod
    def register(cls, driver_class: Type[HeatpumpDriver]) -> Type[HeatpumpDriver]:
        """
        Registers a heat pump driver.

        Can be used as a decorator:
            @ManufacturerRegistry.register
            class MyDriver(HeatpumpDriver):
                MANUFACTURER = "my_brand"
                MODEL = "model_x"

        Args:
            driver_class: The driver class to register

        Returns:
            The driver class (for decorator use)
        """
        mfr = driver_class.MANUFACTURER
        model = driver_class.MODEL

        if not mfr or not model:
            logger.warning(
                f"Driver {driver_class.__name__} missing MANUFACTURER or MODEL"
            )
            return driver_class

        if mfr not in cls._drivers:
            cls._drivers[mfr] = {}

        cls._drivers[mfr][model] = driver_class
        logger.debug(f"Registered driver: {mfr}/{model} -> {driver_class.__name__}")

        return driver_class

    @classmethod
    def get_driver(
        cls, manufacturer: str, model: str, cached: bool = True
    ) -> Optional[HeatpumpDriver]:
        """
        Returns a driver instance for the specified manufacturer and model.

        Args:
            manufacturer: Manufacturer ID (e.g., "idm")
            model: Model ID (e.g., "navigator_2_0")
            cached: If True, return cached instance; if False, create new

        Returns:
            HeatpumpDriver instance or None if not found
        """
        if manufacturer not in cls._drivers:
            logger.warning(f"Unknown manufacturer: {manufacturer}")
            return None

        if model not in cls._drivers[manufacturer]:
            logger.warning(f"Unknown model: {manufacturer}/{model}")
            return None

        cache_key = f"{manufacturer}/{model}"

        if cached and cache_key in cls._instances:
            return cls._instances[cache_key]

        driver_class = cls._drivers[manufacturer][model]
        instance = driver_class()

        if cached:
            cls._instances[cache_key] = instance

        return instance

    @classmethod
    def list_manufacturers(cls) -> List[Dict]:
        """
        Returns a list of all supported manufacturers and their models.

        Returns:
            List of dicts with manufacturer info:
            [
                {
                    "id": "idm",
                    "name": "iDM Energiesysteme",
                    "models": [
                        {"id": "navigator_2_0", "name": "Navigator 2.0"}
                    ]
                }
            ]
        """
        result = []

        for mfr_id, models in sorted(cls._drivers.items()):
            model_list = []
            for model_id, driver_class in sorted(models.items()):
                model_list.append(
                    {
                        "id": model_id,
                        "name": driver_class.DISPLAY_NAME,
                        "protocol": driver_class.PROTOCOL,
                        "default_port": driver_class.DEFAULT_PORT,
                    }
                )

            result.append(
                {
                    "id": mfr_id,
                    "name": cls._manufacturer_names.get(mfr_id, mfr_id.title()),
                    "models": model_list,
                }
            )

        return result

    @classmethod
    def get_manufacturer_name(cls, manufacturer_id: str) -> str:
        """Returns the display name for a manufacturer."""
        return cls._manufacturer_names.get(manufacturer_id, manufacturer_id.title())

    @classmethod
    def is_supported(cls, manufacturer: str, model: str) -> bool:
        """Checks if a manufacturer/model combination is supported."""
        return manufacturer in cls._drivers and model in cls._drivers[manufacturer]

    @classmethod
    def get_all_drivers(cls) -> Dict[str, Dict[str, Type[HeatpumpDriver]]]:
        """Returns the complete driver registry."""
        return cls._drivers.copy()


def _discover_drivers():
    """
    Auto-discovers and imports all driver modules.

    This function is called at module import time to ensure
    all drivers are registered.
    """
    import importlib
    import os

    # Get the directory of this module
    base_dir = os.path.dirname(__file__)

    # List of manufacturer directories to scan
    manufacturers = ["idm", "nibe", "daikin", "luxtronik"]

    for mfr in manufacturers:
        mfr_dir = os.path.join(base_dir, mfr)
        if not os.path.isdir(mfr_dir):
            continue

        # Find Python files in the manufacturer directory
        for filename in os.listdir(mfr_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                try:
                    importlib.import_module(
                        f".{mfr}.{module_name}", package="idm_logger.manufacturers"
                    )
                except ImportError as e:
                    logger.debug(f"Could not import {mfr}/{module_name}: {e}")
                except Exception as e:
                    logger.warning(f"Error importing {mfr}/{module_name}: {e}")


# Discover drivers when module is imported
_discover_drivers()
