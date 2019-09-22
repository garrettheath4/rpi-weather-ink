#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    Image, ImageFont, ImageDraw = None, None, None
    exit("This package requires PIL/Pillow to be installed\nInstall it with: sudo apt install python-pil")

# Transitive dependencies of Inky library
try:
    import spidev
except ImportError:
    print("The inky library probably requires the spidev module\n"
          + "If this package fails to run, install spidev with pipenv install --system")
try:
    import smbus2
except ImportError:
    print("The inky library probably requires the smbus2 module\n"
          + "If this package fails to run, install smbus2 with pipenv install --system")
try:
    import RPi.GPIO
except ImportError:
    print("The inky library probably requires the RPi.GPIO module\n"
          + "If this package fails to run, install RPi.GPIO with sudo apt install python-rpi.gpio")
try:
    import numpy
except ImportError:
    print("The inky library probably requires the numpy module\n"
          + "If this package fails to run, install numpy with sudo apt install python-numpy")

try:
    from inky import InkyPHAT
except ImportError:
    from tests.mock import InkyPHAT
    exit("This package requires the inky module\nInstall it with sudo pip install inky")

from weatherink.fetch.weather import Weather

location_coords = [38.928766, -77.032645]
text_font_filename = "resources/Ubuntu-Regular.ttf"
icons_font_filename = "resources/Font Awesome 5 Free-Solid-900.otf"

# phat-specific (as opposed to what-specific)
COLOR = "yellow"
font_size = 38
scale_size = 1
temp_unit = u"\u00B0F"  # degree F
padding = 10
left_nudge = 20
radiation_icon = u"\uf7ba"
radiation_location = (75 - left_nudge, 6)

icons_font = ImageFont.truetype(icons_font_filename, int(font_size * scale_size))
text_font = ImageFont.truetype(text_font_filename, int(font_size * scale_size))


def run():
    if InkyPHAT is None:
        print("Error: InkyPHAT was not properly imported")
        return
    inky_display = InkyPHAT(COLOR)
    display_size = (InkyPHAT.WIDTH, InkyPHAT.HEIGHT)

    # inky_display.set_rotation(180)
    inky_display.set_border(InkyPHAT.YELLOW)

    img = Image.new("P", display_size)

    weather = Weather(location_coords)
    # TODO: Only update the display if the data has changed since the last refresh
    # (Use a temporary file to save the data for the most recent screen draw)

    draw_text(weather.uv_index,            2, img, display_size)
    draw_text(get_sky_icon(weather),       3, img, display_size, use_icon_font=True)
    draw_text(get_high_temp_copy(weather), 1, img, display_size)
    draw_text(get_low_temp_copy(weather),  4, img, display_size)

    if weather.is_uv_warning():
        ImageDraw.Draw(img).text(radiation_location, radiation_icon, InkyPHAT.YELLOW, font=icons_font)

    # TODO: Show the chance of precipitation next to the sky icon

    inky_display.set_image(img)
    inky_display.show()


def draw_text(text, quadrant, image, display_size, use_icon_font=False):
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


if __name__ == "__main__":
    run()
