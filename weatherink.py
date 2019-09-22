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
    InkyPHAT = lambda x: x
    exit("This script requires the inky module\nInstall it with sudo pip install inky")

try:
    import requests
except ImportError:
    requests = None
    exit("This script requires the requests module\nInstall it with pipenv install --system")

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = lambda x, y: x
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
temp_unit = u"°F"


def main():
    inky_display = InkyPHAT(COLOR)
    display_size = (inky_display.WIDTH, inky_display.HEIGHT)

    # inky_display.set_rotation(180)
    inky_display.set_border(inky_display.RED)

    img = Image.new("P", display_size)

    # Draw vertical line
    for y in range(0, inky_display.height):
        img.putpixel((inky_display.width / 2, y), inky_display.BLACK)

    # Draw horizontal line
    for x in range(0, inky_display.width):
        img.putpixel((x, inky_display.height / 2), inky_display.BLACK)

    weather = Weather(location_coords, get_api_key_from_config())

    draw_text(weather.uv_index_int(),      2, img, display_size)
    draw_text(get_sky_icon(weather),       3, img, display_size, font_awesome=True)
    draw_text(get_high_temp_copy(weather), 1, img, display_size)
    draw_text(get_low_temp_copy(weather),  4, img, display_size)

    inky_display.set_image(img)
    inky_display.show()


def draw_text(text, quadrant, image, display_size, font_awesome=False):
    # intuitive_font = ImageFont.truetype(Intuitive, int(22 * scale_size))
    # hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(35 * scale_size))
    # hanken_medium_font = ImageFont.truetype(HankenGroteskMedium, int(font_size * scale_size))

    if font_awesome:
        draw_font = ImageFont.truetype(fa_filename, int(font_size * scale_size))
    else:
        draw_font = ImageFont.truetype(HankenGroteskMedium, int(font_size * scale_size))

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
        text_x += display_width / 2
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
    if weather.summary_key_str() in icons:
        return icons[weather.summary_key_str()]
    else:
        return question_icon


def get_high_temp_copy(weather):
    return str(weather.high_temp_int()) + temp_unit


def get_low_temp_copy(weather):
    return str(weather.low_temp_int()) + temp_unit


class Weather:
    def __init__(self, coords, api_key=None):
        coords_str = ",".join([str(c) for c in coords])
        self.weather = {}
        if api_key:
            # exclude=currently,minutely,hourly,daily,alerts,flags
            res = requests.get("https://api.darksky.net/forecast/{}/{}?exclude=minutely,hourly,alerts,flags"
                               .format(api_key, coords_str))
            if res.status_code == 200:
                res_json = json.loads(res.content)
                self.weather["summary-key"] = res_json["daily"]["icon"]
                self.weather["current-temp"] = int(round(res_json["currently"]["temperature"]))
                self.weather["feels-like"] = int(round(res_json["currently"]["apparentTemperature"]))
                self.weather["low-temp"] = int(round(res_json["daily"]["data"][0]["temperatureLow"]))
                self.weather["high-temp"] = int(round(res_json["daily"]["data"][0]["temperatureHigh"]))
                self.weather["uv-index"] = int(res_json["daily"]["data"][0]["uvIndex"])
            else:
                raise Exception("API request returned a not-OK status code", res.status_code, res.url)
        else:
            print("Info: Fetching data from current forecast page instead of API since no API key was given")
            res = requests.get("https://darksky.net/forecast/{}/us12/en".format(coords_str))
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "lxml")
                curr = soup.find("span", "currently")
                self.weather["summary-key"] = curr.img["alt"].split()[0]
                self.weather["current-temp"] = int(curr.find("span", "summary").text.split()[0][:-1])
                high_low = curr.find("span", {"class": "summary-high-low"})
                self.weather["feels-like"] = int(high_low.find("span", {"class": "feels-like-text"}).text[:-1])
                self.weather["low-temp"] = int(high_low.find("span", {"class": "low-temp-text"}).text[:-1])
                self.weather["high-temp"] = int(high_low.find("span", {"class": "high-temp-text"}).text[:-1])
                self.weather["uv-index"] = int(soup.find(id="currentDetails")
                                               .find("div", {"class": "uv_index"})
                                               .find("span", {"class": "uv__index__value"})
                                               .text)
            else:
                raise Exception("UI request returned a not-OK status code", res.status_code, res.url)

    def summary_key_str(self):
        return self.weather["summary-key"]

    def current_temp_int(self):
        return self.weather["current-temp"]

    def feels_like_int(self):
        return self.weather["feels-like"]

    def low_temp_int(self):
        return self.weather["low-temp"]

    def high_temp_int(self):
        return self.weather["high-temp"]

    def uv_index_int(self):
        return self.weather["uv-index"]


def get_api_key_from_config():
    config = ConfigParser.RawConfigParser()
    config.read('secrets.ini')
    try:
        return config.get("DarkSky", "api-key")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return None


if __name__ == "__main__":
    main()
