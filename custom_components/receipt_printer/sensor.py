"""Sensor platform for receipt_printer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription

from .const import PAPER_STATUS
from .entity import ReceiptPrinterEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import ReceiptPrinterConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="paper_status",
        name="Paper Status",
        icon="mdi:receipt",
        device_class=SensorDeviceClass.ENUM,
        options=["ok", "low", "out"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ReceiptPrinterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        [
            ReceiptPrinterPaperSensor(
                entry=entry,
                entity_description=entity_description,
            )
            for entity_description in ENTITY_DESCRIPTIONS
        ]
    )


class ReceiptPrinterPaperSensor(ReceiptPrinterEntity, SensorEntity):
    """Receipt Printer Paper Status Sensor class."""

    def __init__(
        self,
        entry: ReceiptPrinterConfigEntry,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(entry)
        self.entity_description = entity_description
        self._attr_unique_id = f"{entry.entry_id}_{entity_description.key}"

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            status = await self._entry.runtime_data.client.async_get_status()
            
            if not status.get("online", False):
                # If printer is offline, mark sensor as unavailable
                self._attr_available = False
            else:
                paper_status = status.get("paper_status", 0)
                if paper_status == 0:
                    self._attr_native_value = "out"
                elif paper_status == 1:
                    self._attr_native_value = "low"
                else:
                    self._attr_native_value = "ok"
                
                self._attr_available = True
        except Exception:
            self._attr_available = False
