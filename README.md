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
sudo apt install python-pil python-rpi.gpio python-numpy python-lxml
cd rpi-weather-ink/
pipenv install --system
```

If you want to use the Dark Sky API to fetch more accurate forecast data, you'll
need to put the Dark Sky API key in a `secrets.ini` file in the `resources/`
folder of this project (the `rpi-weather-ink/` directory). The file should be
formatted like this:

```
[DarkSky]
api-key = 1234567890abcdef0123456789ABCDEF
```


## Running

### Run Once

Just run the `weatherink` module to refresh the e-ink display.

```
cd rpi-weather-ink/
python -m weatherink
```

### Run Automatically

Run `crontab -e` and insert the following line into your crontab file to refresh
the screen every 5 minutes.

```
*/5 * * * * cd $HOME/rpi-weather-ink/ && ( git pull -q ; python -m weatherink )
```


## Features

- Fetches weather forecast data from [Dark Sky API](https://darksky.net/dev)
- Displays weather data on e-ink display
    - UV index
    - Sky forecast icon (e.g. sunny or cloudy)
    - High and low temperatures for the day
- Uses [Font Awesome 5 Free](https://fontawesome.com) for icons
- Uses [Ubuntu](https://design.ubuntu.com/font/) open-source font for text
- Displays warning icon if daily UV index is high (6 or higher by default)
- Refreshes weather data every 5 minutes


## Future Work

- [ ] Only re-render e-ink screen if data has changed since previous render
- [ ] Improve graphic design on screen
- [ ] Show graph of forecasted rainfall in the next few minutes and hours


## Development

### Workflow

```
sudo pip install pipenv
pipenv install <python-package>
pipenv run python -m weatherink
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

When adding new dependencies to this project, try to add them using first
successful method listed below, in order:

1. `pipenv install <package>`
1. `sudo pip install <package>`
1. `sudo apt install <package>`


## Hardware

* Raspberry Pi Zero WH (Zero W with Headers)
* Pimoroni Inky pHAT - 3 Color eInk Display (Yellow/Black/White)
* Adafruit Raspberry Pi Zero Case
* USB On-the-Go Cable (Micro-USB male to USB A female)
* Mini HDMI to HDMI Cable

