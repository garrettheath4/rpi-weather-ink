#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    exit("This script requires PIL/Pillow to be installed\nInstall it with: sudo apt install python-pil")

# Fonts
try:
    from font_hanken_grotesk import HankenGroteskMedium
except ImportError:
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
    from inky import InkyPHAT, InkyWHAT
except ImportError:
    exit("This script requires the inky module\nInstall it with sudo pip install inky")

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall it with pipenv install --system")

try:
    from bs4 import BeautifulSoup
except ImportError:
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
    draw = ImageDraw.Draw(img)

    # Draw vertical line
    for y in range(0, inky_display.height):
        img.putpixel((inky_display.width / 2, y), inky_display.BLACK)

    # Draw horizontal line
    for x in range(0, inky_display.width):
        img.putpixel((x, inky_display.height / 2), inky_display.BLACK)

    weather = Weather(location_coords)

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
    question_icon = u"\uf128"
    icons = {
                "clear-day": sun_icon,
                "clear-night": sun_icon,
                "partly-cloudy-day": cloud_icon,
                "partly-cloudy-night": cloud_icon,
                "cloudy": cloud_icon,
                "rain": rain_icon,
                "sleet": rain_icon,
                "snow": rain_icon,
                "wind": sun_icon,
                "fog": cloud_icon,
            }
    if weather.summary_text() in icons:
        return icons[weather.summary_text()]
    else:
        return question_icon


def get_high_temp_copy(weather):
    return str(weather.high_temp_int()) + temp_unit


def get_low_temp_copy(weather):
    return str(weather.low_temp_int()) + temp_unit


class Weather:
    def __init__(self, coords):
        self.weather = {}
        res = requests.get("https://darksky.net/forecast/{}/us12/en".format(",".join([str(c) for c in coords])))
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "lxml")
            curr = soup.find("span", "currently")
            self.weather["summary"] = curr.img["alt"].split()[0]
            self.weather["current-temp"] = int(curr.find("span", "summary").text.split()[0][:-1])
            high_low = curr.find("span", {"class": "summary-high-low"})
            self.weather["feels-like"] = int(high_low.find("span", {"class": "feels-like-text"}).text[:-1])
            self.weather["low-temp"] = int(high_low.find("span", {"class": "low-temp-text"}).text[:-1])
            self.weather["high-temp"] = int(high_low.find("span", {"class": "high-temp-text"}).text[:-1])
            self.weather["uv-index"] = int(soup.find(id="currentDetails")
                                           .find("div", {"class": "uv_index"})
                                           .find("span", {"class": "uv__index__value"})
                                           .text)

    def summary_text(self):
        return self.weather["summary"]

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


if __name__ == "__main__":
    main()
