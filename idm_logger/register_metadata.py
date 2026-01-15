"""
Register metadata from iDM Navigator 2.0 Modbus documentation.
This module loads register definitions including EEPROM sensitivity and cyclic change requirements.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RegisterMetadata:
    """Manages register metadata from YAML configuration."""

    def __init__(self):
        self._registers = {}
        self._load_metadata()

    def _load_metadata(self):
        """Load register metadata from YAML file."""
        yaml_path = Path(__file__).parent.parent / "idm_navigator_modbus_registers.yaml"

        if not yaml_path.exists():
            logger.warning(f"Register metadata file not found: {yaml_path}")
            return

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if "registers" in data:
                for reg in data["registers"]:
                    address = reg.get("address_dec")
                    if address is not None:
                        self._registers[address] = {
                            "name": reg.get("name", ""),
                            "datatype": reg.get("datatype", ""),
                            "access": reg.get("access", "RO"),
                            "eeprom_sensitive": reg.get("eeprom_sensitive", False),
                            "cyclic_change_required": reg.get(
                                "cyclic_change_required", False
                            ),
                            "unit": reg.get("unit"),
                            "min": reg.get("min"),
                            "max": reg.get("max"),
                            "enum_text": reg.get("enum_text"),
                            "notes": reg.get("notes"),
                        }

            logger.info(f"Loaded metadata for {len(self._registers)} registers")

        except Exception as e:
            logger.error(f"Failed to load register metadata: {e}")

    def get_register_info(self, address: int) -> Optional[Dict]:
        """Get register information by address."""
        return self._registers.get(address)

    def is_eeprom_sensitive(self, address: int) -> bool:
        """Check if register is EEPROM sensitive (limited write cycles)."""
        reg_info = self._registers.get(address)
        if reg_info:
            return reg_info.get("eeprom_sensitive", False)
        return False

    def requires_cyclic_change(self, address: int) -> bool:
        """Check if register requires cyclic changes (e.g., every 10 minutes)."""
        reg_info = self._registers.get(address)
        if reg_info:
            return reg_info.get("cyclic_change_required", False)
        return False

    def get_access_mode(self, address: int) -> str:
        """Get access mode (RO, RW, W, etc.)."""
        reg_info = self._registers.get(address)
        if reg_info:
            return reg_info.get("access", "RO")
        return "RO"


# Global instance
register_metadata = RegisterMetadata()
