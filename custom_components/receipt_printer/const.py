"""Constants for receipt_printer."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "receipt_printer"

# Config flow
CONF_PRINTER_IP = "printer_ip"
CONF_PRINTER_NAME = "printer_name"

# Services
SERVICE_PRINT_TEXT = "print_text"
SERVICE_PRINT_IMAGE = "print_image"
SERVICE_PRINT_QR = "print_qr"

# Paper status
PAPER_STATUS = {
    0: "No Paper",
    1: "Paper Low",
    2: "Paper OK",
}
