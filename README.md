# Picotamachibi
## A Raspberry Pi Pico Powered Virtual Pet

Picotamachibi is a tiny virtual pet built for the Pico-LCD-1.14, featuring animated sprites, a toolbar-driven UI, and timed events that drive sleep, feeding, and health. The project uses PBM assets and MicroPython modules organized under `gui` to keep display and UI logic tidy.

By Kevin McAleer, September 2021

---

This is the code repository that accompanies this video:

[![PicoTamachibi](https://img.youtube.com/vi/c6D1JRDddkE/0.jpg)](https://youtu.be/c6D1JRDddkE)

[![PicoTamachibi Pico-LCD-1.14]](https://youtube.com/shorts/tH2mpzrPVa4)

---

## About this code
To use the code, upload all the `.pbm` files to the pico, the entire `gui` folder (the main app uses `pico_lcd_1_14.py`; `ssd1306.py` is only for the SSD1306 demo), and the main program `picotamachibi.py`.

## Wiring (Pico-LCD-1.14)
Display (SPI1):
1. BL = GPIO 13
2. DC = GPIO 8
3. RST = GPIO 12
4. MOSI = GPIO 11
5. SCK = GPIO 10
6. CS = GPIO 9

Buttons:
1. A = GPIO 15
2. B = GPIO 17
3. Up = GPIO 2
4. Center = GPIO 3
5. Left = GPIO 16
6. Down = GPIO 18
7. Right = GPIO 20

Press A or Left/Right to move the toolbar selector, Center to cancel, and B to select the menu option.

## Getting help
If you have any questions about this, [join our discord](https://action.smarsfan.com/join-discord) server and ask away : )
