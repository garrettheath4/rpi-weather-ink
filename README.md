# Raspberry Pi Weather E-Ink Display

The purpose of this project is to have a digital display to always show an
up-to-date weather forecast including the UV index of the day.

```
+----------|----------+
| UV Index | Hi  Temp |
| Cloudy   | Low Temp |
+----------|----------+
```

## Installation

```
cd rpi-weather-ink/
python setup.py install
```

## Running

Just run the `ink-display.py` script to refresh the e-ink display.

```
cd rpi-weather-ink/
./ink-display.py
```

## Hardware

* Raspberry Pi Zero WH (Zero W with Headers)
* Pimoroni Inky pHAT - 3 Color eInk Display (Yellow/Black/White)
* Adafruit Raspberry Pi Zero Case
* USB On-the-Go Cable (Micro-USB male to USB A female)
* Mini HDMI to HDMI Cable
