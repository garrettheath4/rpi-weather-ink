#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import random

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    exit("This script requires PIL/Pillow to be installed\nInstall it with: sudo apt install python-pil")

# Fonts
try:
    from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
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
    print("The inky library probably requires the spidev module\nIf this script fails, install spidev with pipenv install --system")
try:
    import smbus2
except ImportError:
    print("The inky library probably requires the smbus2 module\nIf this script fails, install smbus2 with pipenv install --system")
try:
    import RPi.GPIO
except ImportError:
    print("The inky library probably requires the RPi.GPIO module\nIf this script fails, install RPi.GPIO with sudo apt install python-rpi.gpio")
try:
    import numpy
except ImportError:
    print("The inky library probably requires the numpy module\nIf this script fails, install numpy with sudo apt install python-numpy")

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
    print("The BeautifulSoup library probably requires the lxml module\nIf this script fails, install lxml with sudo apt install python-lxml")

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

    draw_text(get_uv(),             2, img, display_size)
    draw_text(get_cloudiness(True), 3, img, display_size, font_awesome=True)
    draw_text(get_high_temp_copy(), 1, img, display_size)
    draw_text(get_low_temp_copy(),  4, img, display_size)

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


def get_uv():
    return random.randint(3, 9)


def get_cloudiness(font_awesome=False):
    if font_awesome:
        return random.choice([
            u"\uf185",  # sun
            u"\uf0c2",  # cloud
            u"\uf73d",  # cloud-rain
        ])
    else:
        return random.choice([u"Sunny", u"Cloudy", u"Rain"])


def get_high_temp():
    return random.randint(80, 90)


def get_high_temp_copy():
    return str(get_high_temp()) + temp_unit


def get_low_temp():
    return random.randint(60, 70)


def get_low_temp_copy():
    return str(get_low_temp()) + temp_unit


def get_weather():
    weather = {}
    res = requests.get("https://darksky.net/forecast/{}/us12/en".format(",".join([str(c) for c in location_coords])))
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "lxml")
        curr = soup.find("span", "currently")
        weather["summary"] = curr.img["alt"].split()[0]
        weather["current-temp"] = int(curr.find("span", "summary").text.split()[0][:-1])
        high_low = curr.find("span", { "class": "summary-high-low" })
        weather["feels-like"] = int(high_low.find("span", { "class": "feels-like-text" }).text[:-1])
        weather["low-temp"]   = int(high_low.find("span", { "class": "low-temp-text" }).text[:-1])
        weather["high-temp"]  = int(high_low.find("span", { "class": "high-temp-text" }).text[:-1])
        weather["uv"] = int(soup.find(id="currentDetails") \
            .find("div", { "class": "uv_index" }) \
            .find("span", { "class": "uv__index__value" }) \
            .text)
        return weather
    else:
        return weather


if __name__ == "__main__":
    main()
