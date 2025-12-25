"""Binary sensor platform for receipt_printer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import ReceiptPrinterEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import ReceiptPrinterConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="online",
        name="Online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ReceiptPrinterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    async_add_entities(
        [
            ReceiptPrinterOnlineSensor(
                entry=entry,
                entity_description=entity_description,
            )
            for entity_description in ENTITY_DESCRIPTIONS
        ]
    )


class ReceiptPrinterOnlineSensor(ReceiptPrinterEntity, BinarySensorEntity):
    """Receipt Printer Online Binary Sensor class."""

    def __init__(
        self,
        entry: ReceiptPrinterConfigEntry,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor class."""
        super().__init__(entry)
        self.entity_description = entity_description
        self._attr_unique_id = f"{entry.entry_id}_{entity_description.key}"

    async def async_update(self) -> None:
        """Update the binary sensor."""
        try:
            status = await self._entry.runtime_data.client.async_get_status()
            self._attr_is_on = status.get("online", False)
            self._attr_available = True
        except Exception:
            self._attr_is_on = False
            self._attr_available = False
