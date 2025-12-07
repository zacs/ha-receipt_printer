"""ReceiptPrinterEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import CONF_PRINTER_IP, DOMAIN

if TYPE_CHECKING:
    from .data import ReceiptPrinterConfigEntry


class ReceiptPrinterEntity(Entity):
    """ReceiptPrinterEntity class."""

    _attr_has_entity_name = True

    def __init__(self, entry: ReceiptPrinterConfigEntry) -> None:
        """Initialize."""
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_PRINTER_IP])},
            name=entry.title,
            manufacturer="Epson",
            model="Receipt Printer",
        )
