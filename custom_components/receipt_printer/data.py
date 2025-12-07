"""Custom types for receipt_printer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import ReceiptPrinterApiClient


type ReceiptPrinterConfigEntry = ConfigEntry[ReceiptPrinterData]


@dataclass
class ReceiptPrinterData:
    """Data for the Receipt Printer integration."""

    client: ReceiptPrinterApiClient
    integration: Integration
