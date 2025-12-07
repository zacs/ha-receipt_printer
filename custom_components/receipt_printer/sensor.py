"""Sensor platform for receipt_printer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory

from .const import PAPER_STATUS
from .entity import ReceiptPrinterEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import ReceiptPrinterConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="status",
        name="Status",
        icon="mdi:printer",
        device_class=SensorDeviceClass.ENUM,
        options=["online", "offline", "paper_low", "no_paper"],
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
            ReceiptPrinterStatusSensor(
                entry=entry,
                entity_description=entity_description,
            )
            for entity_description in ENTITY_DESCRIPTIONS
        ]
    )


class ReceiptPrinterStatusSensor(ReceiptPrinterEntity, SensorEntity):
    """Receipt Printer Status Sensor class."""

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
                self._attr_native_value = "offline"
            else:
                paper_status = status.get("paper_status", 0)
                if paper_status == 0:
                    self._attr_native_value = "no_paper"
                elif paper_status == 1:
                    self._attr_native_value = "paper_low"
                else:
                    self._attr_native_value = "online"
            
            self._attr_available = True
        except Exception:
            self._attr_available = False
            self._attr_native_value = "offline"
