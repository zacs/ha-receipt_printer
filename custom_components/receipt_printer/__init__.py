"""
Custom integration to integrate receipt printers with Home Assistant.

For more details about this integration, please refer to
https://github.com/zacs/ha-receipt_printer
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from getmac import get_mac_address
from homeassistant.const import Platform
from homeassistant.core import ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.loader import async_get_loaded_integration

from .api import ReceiptPrinterApiClient
from .const import (
    CONF_COLUMNS_FONT_A,
    CONF_COLUMNS_FONT_B,
    CONF_IMAGE_MAX_WIDTH,
    CONF_PRINTER_IP,
    DOMAIN,
    LOGGER,
    SERVICE_PRINT_IMAGE,
    SERVICE_PRINT_QR,
    SERVICE_PRINT_TEXT,
)
from .data import ReceiptPrinterData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import ReceiptPrinterConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

# Service schemas
SERVICE_PRINT_TEXT_SCHEMA = vol.Schema(
    {
        vol.Required("text"): cv.string,
        vol.Optional("align", default="left"): vol.In(["left", "center", "right"]),
        vol.Optional("font", default="a"): vol.In(["a", "b"]),
        vol.Optional("bold", default=False): cv.boolean,
        vol.Optional("double_height", default=False): cv.boolean,
        vol.Optional("double_width", default=False): cv.boolean,
        vol.Optional("cut", default=True): cv.boolean,
        vol.Optional("wrap", default=True): cv.boolean,
    }
)

SERVICE_PRINT_IMAGE_SCHEMA = vol.Schema(
    {
        vol.Required("image_path"): cv.string,
        vol.Optional("center", default=False): cv.boolean,
        vol.Optional("cut", default=True): cv.boolean,
    }
)

SERVICE_PRINT_QR_SCHEMA = vol.Schema(
    {
        vol.Required("content"): cv.string,
        vol.Optional("size", default=3): vol.All(vol.Coerce(int), vol.Range(min=1, max=16)),
        vol.Optional("center", default=False): cv.boolean,
        vol.Optional("cut", default=True): cv.boolean,
    }
)


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ReceiptPrinterConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    client = ReceiptPrinterApiClient(
        host=entry.data[CONF_PRINTER_IP],
        columns_font_a=entry.data.get(CONF_COLUMNS_FONT_A, 42),
        columns_font_b=entry.data.get(CONF_COLUMNS_FONT_B, 56),
        image_max_width=entry.data.get(CONF_IMAGE_MAX_WIDTH, 400),
    )
    
    entry.runtime_data = ReceiptPrinterData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    # Connect to the printer
    await client.async_connect()

    # Get the MAC address from the IP
    mac_address = get_mac_address(ip=entry.data[CONF_PRINTER_IP])
    
    # Register the device
    device_registry = dr.async_get(hass)
    device_info = {
        "config_entry_id": entry.entry_id,
        "identifiers": {(DOMAIN, entry.data[CONF_PRINTER_IP])},
        "name": entry.title,
        "manufacturer": "Epson",
        "model": "Receipt Printer",
    }
    
    # Only add MAC connection if we successfully retrieved it
    if mac_address:
        device_info["connections"] = {(dr.CONNECTION_NETWORK_MAC, mac_address)}
    
    device_registry.async_get_or_create(**device_info)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register services
    async def handle_print_text(call: ServiceCall) -> None:
        """Handle the print_text service call."""
        await client.async_print_text(
            text=call.data["text"],
            align=call.data["align"],
            font=call.data["font"],
            bold=call.data["bold"],
            double_height=call.data["double_height"],
            double_width=call.data["double_width"],
            cut=call.data["cut"],
            wrap=call.data["wrap"],
        )

    async def handle_print_image(call: ServiceCall) -> None:
        """Handle the print_image service call."""
        await client.async_print_image(
            image_path=call.data["image_path"],
            center=call.data["center"],
            cut=call.data["cut"],
        )

    async def handle_print_qr(call: ServiceCall) -> None:
        """Handle the print_qr service call."""
        await client.async_print_qr(
            content=call.data["content"],
            size=call.data["size"],
            center=call.data["center"],
            cut=call.data["cut"],
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_PRINT_TEXT,
        handle_print_text,
        schema=SERVICE_PRINT_TEXT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_PRINT_IMAGE,
        handle_print_image,
        schema=SERVICE_PRINT_IMAGE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_PRINT_QR,
        handle_print_qr,
        schema=SERVICE_PRINT_QR_SCHEMA,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ReceiptPrinterConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    # Disconnect from the printer
    await entry.runtime_data.client.async_disconnect()
    
    # Unregister services
    hass.services.async_remove(DOMAIN, SERVICE_PRINT_TEXT)
    hass.services.async_remove(DOMAIN, SERVICE_PRINT_IMAGE)
    hass.services.async_remove(DOMAIN, SERVICE_PRINT_QR)
    
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ReceiptPrinterConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
