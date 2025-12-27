"""Constants for receipt_printer."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "receipt_printer"

# Config flow
CONF_PRINTER_IP = "printer_ip"
CONF_PRINTER_NAME = "printer_name"
CONF_COLUMNS_FONT_A = "columns_font_a"
CONF_COLUMNS_FONT_B = "columns_font_b"
CONF_IMAGE_MAX_WIDTH = "image_max_width"

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
