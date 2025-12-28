# Receipt Printer for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

_Integration to control Epson receipt printers in Home Assistant._

## Features

- **Print Services**: Three convenient services for printing:
  - Print text with customizable formatting (alignment, font, bold, double height/width, word wrapping)
  - Print local and remote images (PNG, JPG, GIF, BMP) with automatic resizing
  - Print QR codes
- **Remote Image Support**: Automatically downloads and prints images from URLs
- **Automatic Resizing**: Images are automatically resized to fit your printer's width while maintaining aspect ratio
- **Paper Cutting**: Optional automatic paper cutting after each print job
- **Status Monitoring**: 
  - Binary sensor for online/offline status
  - Sensor for paper status (ok, low, out)
- **Configurable Printer Settings**: Support for different printer models with customizable column widths and image sizes

## Installation

### HACS (Recommended)

1. In HACS, click on "Integrations"
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add the URL `https://github.com/zacs/ha-receipt_printer` and select the category "Integration"
5. Click the "+" button in the bottom right corner
6. Search for "Receipt Printer"
7. Click "Install"
8. Restart Home Assistant

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`)
2. If you do not have a `custom_components` directory there, you need to create it
3. In the `custom_components` directory create a new folder called `receipt_printer`
4. Download all the files from the `custom_components/receipt_printer/` directory in this repository
5. Place the files you downloaded in the new `receipt_printer` directory you created
6. Restart Home Assistant

## Configuration

1. In the Home Assistant UI, navigate to "Configuration" -> "Integrations"
2. Click the "+" button to add a new integration
3. Search for "Receipt Printer"
4. Enter the following information:
   - **Printer Name**: A friendly name for your printer (e.g., "Kitchen Receipt Printer")
   - **Printer IP Address**: The IP address of your receipt printer on your network
   - **Columns (Font A)**: Number of text columns for font A (default: 42, suitable for TM-T88V)
   - **Columns (Font B)**: Number of text columns for font B (default: 56, suitable for TM-T88V)
   - **Image Max Width**: Maximum image width in pixels (default: 512, suitable for TM-T88V)

The integration will attempt to connect to the printer and verify it's accessible. The column and image settings can be adjusted to match your specific printer model.

### Printer Configuration Notes

Different printer models support different widths:
- **Epson TM-T88V/VI** (80mm): Font A = 42 columns, Font B = 56 columns, Image width = 512 pixels
- For other models, consult your printer's documentation or the [python-escpos printer profiles](https://python-escpos.readthedocs.io/en/latest/printer_profiles/available-profiles.html)

## Supported Printers

This integration uses the [python-escpos](https://github.com/python-escpos/python-escpos) library and supports **Epson ESC/POS compatible receipt printers** with network (TCP/IP) connectivity. 

Tested models:
- Epson TM-T88VI

Other ESC/POS compatible printers should work but may require adjusting the column widths and image size settings during configuration.

**Note**: USB and serial printers are not currently supported.

## Usage

### Status Monitoring

Once configured, the integration creates two entities for status monitoring:

#### Binary Sensor: Online Status
- **Connected**: Printer is online and accessible
- **Disconnected**: Cannot communicate with printer

#### Sensor: Paper Status
- **ok**: Printer has adequate paper
- **low**: Paper is running low (near-end sensor triggered)
- **out**: Printer is out of paper

The paper status sensor will be unavailable when the printer is offline.

### Services

The integration provides three services for printing:

#### `receipt_printer.print_text`

Print text to the receipt printer with formatting options.

**Service Data:**
```yaml
service: receipt_printer.print_text
data:
  text: "Hello World!\nThis is a test receipt."
  align: center  # Options: left, center, right
  font: a  # Options: a, b
  bold: false
  double_height: false
  double_width: false
  wrap: true  # Enable automatic word wrapping (default: true)
  cut: true  # Cut paper after printing
```

**Word Wrapping**: When `wrap: true` (default), text will automatically wrap at word boundaries to fit the printer's configured column width. Set to `false` to disable wrapping and print text as-is.

#### `receipt_printer.print_image`

Print an image file to the receipt printer. Images can be local file paths or remote URLs.

**Service Data:**
```yaml
service: receipt_printer.print_image
data:
  image_path: "/config/www/logo.png"  # or "https://example.com/image.jpg"
  center: true
  cut: true
```

**Supported formats**: PNG, JPG, GIF, BMP

**Image Handling**:
- Local files: Use absolute paths (e.g., `/config/www/image.png`)
- Remote images: Use full URLs (e.g., `https://example.com/image.jpg`)
- Images wider than the configured max width are automatically resized while maintaining aspect ratio
- Images smaller than the max width are printed at their original size

#### `receipt_printer.print_qr`

Print a QR code to the receipt printer.

**Service Data:**
```yaml
service: receipt_printer.print_qr
data:
  content: "https://www.home-assistant.io"
  size: 3  # Size from 1-16
  center: true
  cut: true
```

## Example Automations

### Print a welcome message when someone arrives home

```yaml
automation:
  - alias: "Print Welcome Receipt"
    trigger:
      - platform: state
        entity_id: person.john
        to: "home"
    action:
      - service: receipt_printer.print_text
        data:
          text: |
            ================================
                 WELCOME HOME JOHN!
            ================================
            
            Time: {{ now().strftime('%H:%M:%S') }}
            Date: {{ now().strftime('%Y-%m-%d') }}
            
            Temperature: {{ states('sensor.living_room_temperature') }}°C
            
            ================================
          align: center
          cut: true
```

### Print a shopping list QR code

```yaml
automation:
  - alias: "Print Shopping List QR"
    trigger:
      - platform: tag
        tag_id: shopping_list
    action:
      - service: receipt_printer.print_text
        data:
          text: "Scan for Shopping List:"
          align: center
          bold: true
          cut: false
      - service: receipt_printer.print_qr
        data:
          content: "https://your-shopping-list-url.com"
          size: 5
          center: true
          cut: true
```

### Print door access notification

```yaml
automation:
  - alias: "Print Door Access Log"
    trigger:
      - platform: state
        entity_id: lock.front_door
        to: "unlocked"
    action:
      - service: receipt_printer.print_text
        data:
          text: |
            DOOR ACCESS LOG
            {{ now().strftime('%Y-%m-%d %H:%M:%S') }}
            
            Front door unlocked
            {% if trigger.to_state.attributes.user_id %}
            User: {{ trigger.to_state.attributes.user_id }}
            {% endif %}
          align: left
          cut: true
```

## Troubleshooting

### Printer not connecting

1. Verify the printer's IP address is correct
2. Ensure the printer is powered on and connected to your network
3. Check that your Home Assistant instance can reach the printer's IP (try pinging it)
4. Verify no firewall is blocking communication on the printer's port (typically 9100)

### Print quality issues

- Clean the printer's print head according to manufacturer instructions
- Check paper quality and ensure it's compatible with thermal printing
- Verify paper is loaded correctly

### Paper status not updating

The paper status depends on the printer's sensors. Some printer models may not support all status queries. The integration will still function for printing even if status updates are unavailable.

## Development

This integration is built using the [python-escpos](https://python-escpos.readthedocs.io/) library. Contributions are welcome!

## Support

- [Report a Bug](https://github.com/zacs/ha-receipt_printer/issues/new?template=bug_report.yml)
- [Request a Feature](https://github.com/zacs/ha-receipt_printer/issues/new?template=feature_request.yml)

## Credits

- Built on top of the [python-escpos](https://github.com/python-escpos/python-escpos) library
- Integration structure based on [integration_blueprint](https://github.com/ludeeus/integration_blueprint)

### Notes

Epson spec sheet for the TM-T88VI (the only model I have): https://download4.epson.biz/sec_pubs/pos/reference_en/epos_and/ref_epos_sdk_and_en_printer-specificsupportinformation_tm-t88vi.html

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/zacs/ha-receipt_printer.svg?style=for-the-badge
[commits]: https://github.com/zacs/ha-receipt_printer/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/zacs/ha-receipt_printer.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/zacs/ha-receipt_printer.svg?style=for-the-badge
[releases]: https://github.com/zacs/ha-receipt_printer/releases
