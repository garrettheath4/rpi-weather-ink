#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import json

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    Image, ImageFont, ImageDraw = None, None, None
    exit("This script requires PIL/Pillow to be installed\nInstall it with: sudo apt install python-pil")

# Fonts
try:
    from font_hanken_grotesk import HankenGroteskMedium
except ImportError:
    HankenGroteskMedium = None
    exit("This script requires the font_hanken_grotesk module\nInstall it with pipenv install --system")
try:
    from font_intuitive import Intuitive
except ImportError:
    exit("This script requires the font_intuitive module\nInstall it with pipenv install --system")

# Transitive dependencies of Inky library
try:
    import spidev
except ImportError:
    print("The inky library probably requires the spidev module\n"
          + "If this script fails, install spidev with pipenv install --system")
try:
    import smbus2
except ImportError:
    print("The inky library probably requires the smbus2 module\n"
          + "If this script fails, install smbus2 with pipenv install --system")
try:
    import RPi.GPIO
except ImportError:
    print("The inky library probably requires the RPi.GPIO module\n"
          + "If this script fails, install RPi.GPIO with sudo apt install python-rpi.gpio")
try:
    import numpy
except ImportError:
    print("The inky library probably requires the numpy module\n"
          + "If this script fails, install numpy with sudo apt install python-numpy")

try:
    from inky import InkyPHAT
except ImportError:
    from tests.mock import InkyPHAT
    exit("This script requires the inky module\nInstall it with sudo pip install inky")

try:
    import requests
except ImportError:
    requests = None
    exit("This script requires the requests module\nInstall it with pipenv install --system")

try:
    from bs4 import BeautifulSoup
except ImportError:
    from tests.mock import BeautifulSoup
    exit("This script requires the BeautifulSoup module\nInstall it with pipenv install --system")

try:
    import lxml
except ImportError:
    print("The BeautifulSoup library probably requires the lxml module\n"
          + "If this script fails, install lxml with sudo apt install python-lxml")

location_coords = [38.928766, -77.032645]
fa_filename = "Font Awesome 5 Free-Solid-900.otf"

# phat-specific (as opposed to what-specific)
COLOR = "yellow"
font_size = 38
scale_size = 1
temp_unit = u"\u2109"
left_pull = 20
radiation_icon = u"\uf7ba"
radiation_location = (75 - left_pull, 6)

fontawesome_font = ImageFont.truetype(fa_filename, int(font_size * scale_size))
hanken_grotesk_font = ImageFont.truetype(HankenGroteskMedium, int(font_size * scale_size))


def run():
    if InkyPHAT is None:
        print("Error: InkyPHAT was not properly imported")
        return
    inky_display = InkyPHAT(COLOR)
    display_size = (InkyPHAT.WIDTH, InkyPHAT.HEIGHT)

    # inky_display.set_rotation(180)
    inky_display.set_border(InkyPHAT.YELLOW)

    img = Image.new("P", display_size)

    weather = Weather(location_coords, get_api_key_from_config())
    # TODO: Only update the display if the data has changed since the last refresh
    # (Use a temporary file to save the data for the most recent screen draw)

    draw_text(weather.uv_index,            2, img, display_size)
    draw_text(get_sky_icon(weather),       3, img, display_size, font_awesome=True)
    draw_text(get_high_temp_copy(weather), 1, img, display_size)
    draw_text(get_low_temp_copy(weather),  4, img, display_size)

    if weather.uv_index > 5:
        ImageDraw.Draw(img).text(radiation_location, radiation_icon, InkyPHAT.YELLOW, font=fontawesome_font)

    # TODO: Show the chance of precipitation next to the sky icon

    inky_display.set_image(img)
    inky_display.show()


def draw_text(text, quadrant, image, display_size, font_awesome=False):
    if font_awesome:
        draw_font = fontawesome_font
    else:
        draw_font = hanken_grotesk_font

    # Ensure baselines line up by always calculating font height including cap
    # line height and descender line height (i.e. vertically align "ab" as if it
    # were as high as "Ay")
    _, font_height = draw_font.getsize("Ay")

    display_width, display_height = display_size

    text_str = text
    if type(text) not in (unicode, str):
        text_str = str(text)

    text_w, text_h = draw_font.getsize(text_str)
    text_x = int(max((display_width / 2) - text_w, 0) / 2)
    if quadrant in (1, 4):
        # TODO: Right-align text instead of centering in quadrant
        text_x += display_width / 2
    else:
        text_x -= left_pull
    text_y = int(max((display_height / 2) - font_height, 0) / 2)
    if quadrant in (3, 4):
        text_y += display_height / 2

    ImageDraw.Draw(image).text((text_x, text_y), text_str, InkyPHAT.BLACK, font=draw_font)


def get_sky_icon(weather):
    sun_icon = u"\uf185"
    cloud_icon = u"\uf0c2"
    rain_icon = u"\uf73d"
    moon_icon = u"\uf186"
    cloud_moon_icon = u"\uf6c3"
    snowflake_icon = u"\uf2dc"
    wind_icon = u"\uf72e"
    smog_icon = u"\uf75f"
    question_icon = u"\uf128"
    icons = {
        "clear-day": sun_icon,
        "clear-night": moon_icon,
        "partly-cloudy-day": cloud_icon,
        "partly-cloudy-night": cloud_moon_icon,
        "cloudy": cloud_icon,
        "rain": rain_icon,
        "sleet": snowflake_icon,
        "snow": snowflake_icon,
        "wind": wind_icon,
        "fog": smog_icon,
    }
    if weather.summary_key in icons:
        return icons[weather.summary_key]
    else:
        return question_icon


def get_high_temp_copy(weather):
    return str(weather.high_temp) + temp_unit


def get_low_temp_copy(weather):
    return str(weather.low_temp) + temp_unit


class Weather:
    def __init__(self, coords, api_key=None):
        self.coords = coords
        self._coords_str = ",".join([str(c) for c in coords])
        self.summary_key = None
        self.current_temp = None
        self.feels_like = None
        self.low_temp = None
        self.high_temp = None
        self.uv_index = None
        if api_key:
            # exclude=currently,minutely,hourly,daily,alerts,flags
            res = requests.get("https://api.darksky.net/forecast/{}/{}?exclude=minutely,hourly,alerts,flags"
                               .format(api_key, self._coords_str))
            if res.status_code == 200:
                res_json = json.loads(res.content)
                self.summary_key = res_json["daily"]["icon"]
                self.current_temp = int(round(res_json["currently"]["temperature"]))
                self.feels_like = int(round(res_json["currently"]["apparentTemperature"]))
                self.low_temp = int(round(res_json["daily"]["data"][0]["temperatureLow"]))
                self.high_temp = int(round(res_json["daily"]["data"][0]["temperatureHigh"]))
                self.uv_index = int(res_json["daily"]["data"][0]["uvIndex"])
            else:
                raise Exception("API request returned a not-OK status code", res.status_code, res.url)
        else:
            print("Info: Fetching data from current forecast page instead of API since no API key was given")
            res = requests.get("https://darksky.net/forecast/{}/us12/en".format(self._coords_str))
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "lxml")
                curr = soup.find("span", "currently")
                self.summary_key = curr.img["alt"].split()[0]
                self.current_temp = int(curr.find("span", "summary").text.split()[0][:-1])
                high_low = curr.find("span", {"class": "summary-high-low"})
                self.feels_like = int(high_low.find("span", {"class": "feels-like-text"}).text[:-1])
                self.low_temp = int(high_low.find("span", {"class": "low-temp-text"}).text[:-1])
                self.high_temp = int(high_low.find("span", {"class": "high-temp-text"}).text[:-1])
                self.uv_index = int(soup.find(id="currentDetails")
                                    .find("div", {"class": "uv_index"})
                                    .find("span", {"class": "uv__index__value"})
                                    .text)
            else:
                raise Exception("UI request returned a not-OK status code", res.status_code, res.url)


def get_api_key_from_config():
    config = ConfigParser.RawConfigParser()
    config.read('secrets.ini')
    try:
        return config.get("DarkSky", "api-key")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return None


if __name__ == "__main__":
    run()
