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
sudo apt install python-pil
pipenv install
cd rpi-weather-ink/
python setup.py install
```

## Running

Just run the `weatherink.py` script to refresh the e-ink display.

```
cd rpi-weather-ink/
./weatherink.py
```

## Development

### Workflow

```
sudo pip install pipenv
pipenv install <python-package>
pipenv run python weatherink.py
pipenv lock -r > requirements.txt
sudo pip install -r requirements.txt
```

### Linking System Packages

Some libraries are not available to be installed with the typical
`pip install <package>` command and have to be installed with the system's
package manager (i.e. `sudo apt install <package>`). In order to use those
system libraries in a virtualenv environment (like pipenv does), you need to
install them with `apt` and then link them into this project's virtualenv
directory.

```
sudo apt install python-pil
mkdir ~/.local/share/virtualenvs/rpi-weather-ink-T1XSpv21/lib/python2.7/dist-packages
ln -s /usr/lib/python2.7/dist-packages/PIL ~/.local/share/virtualenvs/rpi-weather-ink-T1XSpv21/lib/python2.7/dist-packages/PIL
```

## Hardware

* Raspberry Pi Zero WH (Zero W with Headers)
* Pimoroni Inky pHAT - 3 Color eInk Display (Yellow/Black/White)
* Adafruit Raspberry Pi Zero Case
* USB On-the-Go Cable (Micro-USB male to USB A female)
* Mini HDMI to HDMI Cable
