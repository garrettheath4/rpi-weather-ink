#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import ConfigParser

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    Image, ImageFont, ImageDraw = None, None, None
    exit("This package requires PIL/Pillow to be installed. Install it with: sudo apt install python-pil")

# Transitive dependencies of Inky library
try:
    import spidev
except ImportError:
    print("Warning: The inky library probably requires the spidev module. "
          + "If this package fails to run, install spidev with pipenv install --system")
try:
    import smbus2
except ImportError:
    print("Warning: The inky library probably requires the smbus2 module. "
          + "If this package fails to run, install smbus2 with pipenv install --system")
try:
    import RPi.GPIO
except ImportError:
    print("Warning: The inky library probably requires the RPi.GPIO module. "
          + "If this package fails to run, install RPi.GPIO with sudo apt install python-rpi.gpio")
try:
    import numpy
except ImportError:
    print("Warning: The inky library probably requires the numpy module. "
          + "If this package fails to run, install numpy with sudo apt install python-numpy")

try:
    from inky import InkyPHAT
except ImportError:
    from tests.mock import InkyPHAT
    if os.path.exists("/sys/firmware/devicetree/base/model"):
        print("Warning: This package requires the inky module. Install it with sudo pip install inky")

# Modules from this project
from weatherink.fetch.weather import Weather

# User settings
location_coords = [38.928766, -77.032645]
configuration_filename = "resources/application.ini"

# App resources
text_font_filename = "resources/Ubuntu-Regular.ttf"
icons_font_filename = "resources/Font Awesome 5 Free-Solid-900.otf"

# phat-specific (as opposed to what-specific)
COLOR = "red"
font_size = 40
scale_size = 1
temp_unit = u"\u00B0F"  # degree F
padding = 10
left_nudge = 20
up_text_nudge = 5
radiation_icon = u"\uf7ba"
radiation_location = (75 - left_nudge, 6)

icons_font = ImageFont.truetype(icons_font_filename, int(font_size * scale_size))
text_font = ImageFont.truetype(text_font_filename, int(font_size * scale_size))


def get_debug_from_config():
    config = ConfigParser.RawConfigParser()
    successful = config.read(configuration_filename)
    if not successful:
        return False
    try:
        return config.getboolean("weatherink", "debug")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return False


def run():
    debug = get_debug_from_config()

    inky_display = InkyPHAT(COLOR)
    display_size = (InkyPHAT.WIDTH, InkyPHAT.HEIGHT)

    # inky_display.set_rotation(180)
    inky_display.set_border(InkyPHAT.RED)

    img = Image.new("P", display_size, color=(255 if debug else 0))
    palletize(img)
    image_draw = ImageDraw.Draw(img)

    weather = Weather(location_coords)

    draw_text(weather.uv_index,            2, image_draw, display_size, debug=debug)
    draw_text(get_sky_icon(weather),       3, image_draw, display_size, use_icon_font=True, debug=debug)
    draw_text(get_high_temp_copy(weather), 1, image_draw, display_size, debug=debug)
    draw_text(get_low_temp_copy(weather),  4, image_draw, display_size, debug=debug)

    if weather.is_uv_warning():
        image_draw.text(radiation_location, radiation_icon, InkyPHAT.RED, font=icons_font)

    inky_display.set_image(img)
    inky_display.show()


def palletize(image):
    black = [0, 0, 0]
    white = [255, 255, 255]
    red = [255, 0, 0]
    image.putpalette((white + black + red) * 85 + white)


def draw_text(text, quadrant, image_draw, display_size, use_icon_font=False, debug=False):
    text_str = text
    if type(text) not in (unicode, str):
        text_str = str(text)

    if use_icon_font:
        draw_font = icons_font
        _, font_height = draw_font.getsize(text_str)
    else:
        draw_font = text_font
        # Ensure baselines line up by always calculating font height including cap
        # line height (i.e. vertically align "ao" as if it were as high as "AO")
        _, font_height = draw_font.getsize("F")

    display_width, display_height = display_size

    text_w, text_h = draw_font.getsize(text_str)
    text_x = int(max((display_width / 2) - text_w, 0))
    if quadrant in (1, 4):
        # Right-align
        text_x += display_width / 2 - padding
    else:
        # Center and then nudge left
        text_x /= 2
        text_x += padding - left_nudge
    text_y = int(max((display_height / 2) - font_height, 0) / 2)
    if quadrant in (3, 4):
        text_y += display_height / 2

    if use_icon_font:
        image_draw.text((text_x, text_y), text_str, InkyPHAT.BLACK, font=draw_font)
    else:
        image_draw.text((text_x, text_y - up_text_nudge), text_str, InkyPHAT.BLACK, font=draw_font)

    if debug:
        image_draw.rectangle([(text_x, text_y), (text_x + text_w, text_y + text_h)],
                             outline=InkyPHAT.RED,
                             width=2)


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


if __name__ == "__main__":
    run()
