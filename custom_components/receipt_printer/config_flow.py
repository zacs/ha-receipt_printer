"""Adds config flow for Receipt Printer."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .api import (
    ReceiptPrinterApiClient,
    ReceiptPrinterApiClientCommunicationError,
    ReceiptPrinterApiClientError,
)
from .const import (
    CONF_COLUMNS_FONT_A,
    CONF_COLUMNS_FONT_B,
    CONF_IMAGE_MAX_WIDTH,
    CONF_PRINTER_IP,
    CONF_PRINTER_NAME,
    DOMAIN,
    LOGGER,
)


class ReceiptPrinterFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Receipt Printer."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> ReceiptPrinterOptionsFlowHandler:
        """Get the options flow for this handler."""
        return ReceiptPrinterOptionsFlowHandler()

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
                    vol.Optional(
                        CONF_COLUMNS_FONT_A,
                        default=(user_input or {}).get(CONF_COLUMNS_FONT_A, 42),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_COLUMNS_FONT_B,
                        default=(user_input or {}).get(CONF_COLUMNS_FONT_B, 56),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_IMAGE_MAX_WIDTH,
                        default=(user_input or {}).get(CONF_IMAGE_MAX_WIDTH, 512),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=1000,
                            mode=selector.NumberSelectorMode.BOX,
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


class ReceiptPrinterOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Receipt Printer."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_COLUMNS_FONT_A,
                        default=self.config_entry.options.get(
                            CONF_COLUMNS_FONT_A,
                            self.config_entry.data.get(CONF_COLUMNS_FONT_A, 42),
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_COLUMNS_FONT_B,
                        default=self.config_entry.options.get(
                            CONF_COLUMNS_FONT_B,
                            self.config_entry.data.get(CONF_COLUMNS_FONT_B, 56),
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_IMAGE_MAX_WIDTH,
                        default=self.config_entry.options.get(
                            CONF_IMAGE_MAX_WIDTH,
                            self.config_entry.data.get(CONF_IMAGE_MAX_WIDTH, 512),
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=1000,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
        )
