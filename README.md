# Raspberry Pi Weather E-Ink Display

The purpose of this project is to have a digital display to always show an
up-to-date weather forecast including the UV index of the day.

![Demo of e-ink display](example.png?raw=true)


## Installation

1. Install [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) on a
   Raspberry Pi Zero WH (or similar Raspberry Pi model)
2. Connect the Pimoroni Inky pHAT to the headers on the Raspbery Pi
3. Update the software and install Git and a few required system libraries:

        sudp apt update && sudo apt upgrade
        sudo apt install git python-pil python-rpi.gpio python-numpy python-lxml

4. Clone this repository and install the required Python libraries:

        git clone https://github.com/garrettheath4/rpi-weather-ink.git
        cd rpi-weather-ink/
        pipenv install --system

### Dark Sky API Key

If you want to use the Dark Sky API to fetch more accurate forecast data, you'll
need to put the Dark Sky API key in a `secrets.ini` file in the `resources/`
folder of this project (the `rpi-weather-ink/` directory). If you do not provide
an API key, only partial forecast data can be fetched by scraping the Dark Sky
forecast web page. The _secrets_ file should be formatted like this:

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
- Only re-render e-ink screen if data has changed since previous render


## Future Work

- [ ] Add code to center an icon at a specific X,Y coordinate on the screen
- [ ] Show sunglasses icon if it's sunny _right now_ (current UV index is high
      instead of daily UV index)
- [ ] Show "unplugged" icon if it's offline or unable to reach Dark Sky
- [ ] Show chance of precipitation next to the sky icon
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

