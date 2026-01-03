"""Receipt Printer API Client."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import aiohttp
from PIL import Image

from escpos.printer import Network
from escpos.exceptions import Error as EscposError


class ReceiptPrinterApiClientError(Exception):
    """Exception to indicate a general API error."""


class ReceiptPrinterApiClientCommunicationError(
    ReceiptPrinterApiClientError,
):
    """Exception to indicate a communication error."""


class ReceiptPrinterApiClient:
    """Receipt Printer API Client."""

    def __init__(
        self,
        host: str,
        columns_font_a: int = 42,
        columns_font_b: int = 56,
        image_max_width: int = 512,
    ) -> None:
        """Initialize the Receipt Printer API Client."""
        self._host = host
        self._printer: Network | None = None
        self._columns_font_a = columns_font_a
        self._columns_font_b = columns_font_b
        self._image_max_width = image_max_width

    def _get_printer(self) -> Network:
        """Get or create printer instance."""
        if self._printer is None:
            self._printer = Network(self._host)
        return self._printer

    async def async_connect(self) -> None:
        """Connect to the printer."""
        try:
            await asyncio.to_thread(self._connect)
        except Exception as exception:
            msg = f"Error connecting to printer - {exception}"
            raise ReceiptPrinterApiClientCommunicationError(msg) from exception

    def _connect(self) -> None:
        """Connect to printer (blocking)."""
        printer = self._get_printer()
        printer.open()

    async def async_disconnect(self) -> None:
        """Disconnect from the printer."""
        if self._printer is not None:
            try:
                await asyncio.to_thread(self._printer.close)
            except Exception:
                pass  # Ignore errors on disconnect

    async def async_test_connection(self) -> dict[str, Any]:
        """Test connection and get basic printer info."""
        try:
            return await asyncio.to_thread(self._test_connection)
        except Exception as exception:
            msg = f"Error testing printer connection - {exception}"
            raise ReceiptPrinterApiClientCommunicationError(msg) from exception

    def _test_connection(self) -> dict[str, Any]:
        """Test connection (blocking)."""
        printer = self._get_printer()
        try:
            printer.open()
            # Try to get printer status
            is_online = printer.is_online()
            paper = printer.paper_status()
            
            return {
                "online": is_online,
                "paper_status": paper,
            }
        finally:
            try:
                printer.close()
            except Exception:
                pass

    async def async_get_status(self) -> dict[str, Any]:
        """Get printer status."""
        try:
            return await asyncio.to_thread(self._get_status)
        except Exception as exception:
            msg = f"Error getting printer status - {exception}"
            raise ReceiptPrinterApiClientCommunicationError(msg) from exception

    def _get_status(self) -> dict[str, Any]:
        """Get status (blocking)."""
        printer = self._get_printer()
        try:
            is_online = printer.is_online()
            paper = printer.paper_status()
            
            return {
                "online": is_online,
                "paper_status": paper,
            }
        except EscposError as exception:
            return {
                "online": False,
                "paper_status": 0,
                "error": str(exception),
            }

    async def async_print_text(
        self,
        text: str,
        align: str = "left",
        font: str = "a",
        bold: bool = False,
        double_height: bool = False,
        double_width: bool = False,
        cut: bool = True,
        wrap: bool = True,
    ) -> None:
        """Print text."""
        try:
            await asyncio.to_thread(
                self._print_text,
                text,
                align,
                font,
                bold,
                double_height,
                double_width,
                cut,
                wrap,
            )
        except Exception as exception:
            msg = f"Error printing text - {exception}"
            raise ReceiptPrinterApiClientCommunicationError(msg) from exception

    def _print_text(
        self,
        text: str,
        align: str,
        font: str,
        bold: bool,
        double_height: bool,
        double_width: bool,
        cut: bool,
        wrap: bool,
    ) -> None:
        """Print text (blocking)."""
        printer = self._get_printer()
        printer.set(
            align=align,
            font=font,
            bold=bold,
            double_height=double_height,
            double_width=double_width,
        )
        
        if wrap:
            # Use block_text for automatic word wrapping
            # Use configured column widths
            columns = self._columns_font_b if font == "b" else self._columns_font_a
            # Adjust columns for double width
            if double_width:
                columns = columns // 2
            # Process each line separately to preserve newlines
            for line in text.split("\n"):
                if line:
                    printer.block_text(line, font=font, columns=columns)
                else:
                    # Empty line - print a newline
                    printer.text("\n")
        else:
            # Use regular text without wrapping
            printer.text(text + "\n")
        
        if cut:
            printer.cut()

    async def async_print_image(
        self,
        image_path: str,
        center: bool = False,
        cut: bool = True,
    ) -> None:
        """Print an image."""
        try:
            # Check if image_path is a URL
            if self._is_url(image_path):
                # Download the image to a temporary file
                temp_file = await self._download_image(image_path)
                try:
                    await asyncio.to_thread(
                        self._print_image,
                        temp_file,
                        center,
                        cut,
                    )
                finally:
                    # Clean up the temporary file
                    try:
                        Path(temp_file).unlink()
                    except Exception:
                        pass  # Ignore cleanup errors
            else:
                await asyncio.to_thread(
                    self._print_image,
                    image_path,
                    center,
                    cut,
                )
        except Exception as exception:
            msg = f"Error printing image - {exception}"
            raise ReceiptPrinterApiClientCommunicationError(msg) from exception

    def _is_url(self, path: str) -> bool:
        """Check if a path is a URL."""
        try:
            result = urlparse(path)
            return result.scheme in ("http", "https")
        except Exception:
            return False

    async def _download_image(self, url: str) -> str:
        """Download an image from a URL to a temporary file."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    msg = f"Failed to download image from {url}: HTTP {response.status}"
                    raise ReceiptPrinterApiClientCommunicationError(msg)
                
                # Create a temporary file
                suffix = Path(urlparse(url).path).suffix or ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(await response.read())
                    return tmp_file.name

    def _print_image(
        self,
        image_path: str,
        center: bool,
        cut: bool,
    ) -> None:
        """Print image (blocking)."""
        printer = self._get_printer()
        
        # Open the image and resize if needed
        img = Image.open(image_path)
        
        # Check if image width exceeds configured max width
        if img.width > self._image_max_width:
            # Calculate new height to maintain aspect ratio
            aspect_ratio = img.height / img.width
            new_width = int(self._image_max_width)
            new_height = int(new_width * aspect_ratio)
            
            # Resize the image
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Print the image (escpos supports PIL Image objects)
        printer.image(img, center=center)
        if cut:
            printer.cut()

    async def async_print_qr(
        self,
        content: str,
        size: int = 3,
        center: bool = False,
        cut: bool = True,
    ) -> None:
        """Print a QR code."""
        try:
            await asyncio.to_thread(
                self._print_qr,
                content,
                size,
                center,
                cut,
            )
        except Exception as exception:
            msg = f"Error printing QR code - {exception}"
            raise ReceiptPrinterApiClientCommunicationError(msg) from exception

    def _print_qr(
        self,
        content: str,
        size: int,
        center: bool,
        cut: bool,
    ) -> None:
        """Print QR code (blocking)."""
        printer = self._get_printer()
        printer.qr(content, size=size, center=center)
        if cut:
            printer.cut()
