"""Adds config flow for Receipt Printer."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .api import (
    ReceiptPrinterApiClient,
    ReceiptPrinterApiClientCommunicationError,
    ReceiptPrinterApiClientError,
)
from .const import CONF_PRINTER_IP, CONF_PRINTER_NAME, DOMAIN, LOGGER


class ReceiptPrinterFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Receipt Printer."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connection(
                    host=user_input[CONF_PRINTER_IP],
                )
            except ReceiptPrinterApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except ReceiptPrinterApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                # Use the printer IP as the unique ID
                await self.async_set_unique_id(user_input[CONF_PRINTER_IP])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_PRINTER_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PRINTER_NAME,
                        default=(user_input or {}).get(CONF_PRINTER_NAME, "Receipt Printer"),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        CONF_PRINTER_IP,
                        default=(user_input or {}).get(CONF_PRINTER_IP, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_connection(self, host: str) -> None:
        """Validate we can connect to the printer."""
        client = ReceiptPrinterApiClient(host=host)
        await client.async_test_connection()
