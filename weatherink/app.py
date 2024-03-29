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
from forecast import Weather

# User settings
location_coords = [38.928766, -77.032645]
configuration_filename = "resources/application.ini"

# App resources
text_font_path = "resources/Ubuntu-Regular.ttf"
icons_font_path = "resources/Font Awesome 5 Free-Solid-900.otf"

# phat-specific (as opposed to what-specific)
COLOR = "red"
font_size = 40
scale_size = 1
temp_unit = u"\u00B0F"  # degree F
left_nudge = 20
up_text_nudge = 4
radiation_icon = u"\uf7ba"
radiation_location = (75 - left_nudge, 6)

icons_font = ImageFont.truetype(icons_font_path, int(font_size * scale_size))
text_font = ImageFont.truetype(text_font_path, int(font_size * scale_size))


def get_debug_from_config():
    config = ConfigParser.RawConfigParser()
    successful = config.read(configuration_filename)
    if not successful:
        return False
    try:
        return config.getboolean("weatherink", "debug")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return False


DEBUG = get_debug_from_config()


def run():

    inky_display = InkyPHAT(COLOR)

    # inky_display.set_rotation(180)
    inky_display.set_border(InkyPHAT.RED)

    img = Image.new("P", (InkyPHAT.WIDTH, InkyPHAT.HEIGHT))
    palletize(img)
    image_draw = ImageDraw.Draw(img)

    if DEBUG:
        # Draw vertical line
        for y in xrange(InkyPHAT.HEIGHT):
            img.putpixel((InkyPHAT.WIDTH / 2, y), inky_display.RED)
            img.putpixel((InkyPHAT.WIDTH / 4, y), inky_display.RED)

        # Draw horizontal line
        for x in xrange(InkyPHAT.WIDTH):
            img.putpixel((x, InkyPHAT.HEIGHT / 2), inky_display.RED)

    weather = Weather(location_coords)

    if weather.is_same_as_temp_data():
        if DEBUG:
            print("Not updating the display since the forecast is the same as last time")
        weather.save_temp_forecast(only_if_no_such_file=True)
        return
    else:
        if DEBUG:
            print("Updating display since the forecast has changed since the last render")
        weather.save_temp_forecast()

    draw_text(image_draw, 2, "UV",                        "l")
    draw_text(image_draw, 2, weather.uv_index,            "r",
              color=InkyPHAT.RED if weather.is_uv_warning() else InkyPHAT.BLACK)
    draw_text(image_draw, 1, get_high_temp_copy(weather), "c")
    draw_text(image_draw, 4, get_low_temp_copy(weather),  "c")

    if weather.precipitation_is_likely():
        precip_chance_str = str(int(round(weather.current_precip_probability * 100))) + "%"
        draw_text(image_draw, 3, get_sky_icon(weather), "l", is_icon=True)
        draw_text(image_draw, 3, precip_chance_str,     "r", is_icon=False)
    else:
        draw_text(image_draw, 3, get_sky_icon(weather), "c", is_icon=True)

    inky_display.set_image(img)
    inky_display.show()

    if DEBUG:
        print(weather.eink_data_string())


def palletize(image):
    white = [255, 255, 255]
    black = [0, 0, 0]
    red = [255, 0, 0]
    out_of_bounds_blue = [0, 0, 255]
    image.putpalette(white + black + red + out_of_bounds_blue * 253)


def draw_text(image_draw, quadrant, text, align="c", is_icon=False, color=InkyPHAT.BLACK):
    text_str = text
    if type(text) not in (unicode, str):
        text_str = str(text)

    if is_icon:
        draw_font = icons_font
    else:
        draw_font = text_font

    text_w, text_h = draw_font.getsize(text_str)

    if align.lower().startswith("l"):
        # Center in the LEFT half of the left quadrant
        text_x = int((InkyPHAT.WIDTH / 4 - text_w) / 2)
    elif align.lower().startswith("r"):
        # Center in the RIGHT half of the left quadrant
        text_x = int((InkyPHAT.WIDTH / 4 - text_w) / 2 + InkyPHAT.WIDTH / 4)
    else:
        # Center in left quadrant by default
        text_x = int((InkyPHAT.WIDTH / 2 - text_w) / 2)
    if quadrant in (1, 4):
        text_x += InkyPHAT.WIDTH / 2

    text_y = int(max((InkyPHAT.HEIGHT / 2) - text_h, 0) / 2)
    if quadrant in (3, 4):
        text_y += InkyPHAT.HEIGHT / 2

    if is_icon:
        image_draw.text((text_x, text_y), text_str, color, font=draw_font)
    else:
        image_draw.text((text_x, text_y - up_text_nudge), text_str, color, font=draw_font)

    if DEBUG:
        image_draw.rectangle([(text_x, text_y), (text_x + text_w, text_y + text_h)],
                             outline=InkyPHAT.RED,
                             width=1)


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
