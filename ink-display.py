#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import random

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    exit("This script requires PIL/Pillow to be installed\nInstall it with: sudo apt install python-pil")

try:
    from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
except ImportError:
    exit("This script requires the font_hanken_grotesk module\nInstall it with pipenv install --system")

try:
    from font_intuitive import Intuitive
except ImportError:
    exit("This script requires the font_intuitive module\nInstall it with pipenv install --system")

try:
    from inky import InkyPHAT, InkyWHAT
except ImportError:
    exit("This script requires the inky module\nInstall it with pipenv install --system")

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

    # TODO: Draw background (white?)

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
        draw_font = ImageFont.truetype('Font Awesome 5 Free-Regular-400.otf', int(font_size * scale_size))
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
    # TODO: Draw a sun, cloud, or rain instead of words
    if font_awesome:
        return random.choice([u"\uf185", u"\uf0c2"])
    else:
        return random.choice([u"Sunny", u"Cloudy"])


def get_high_temp():
    return random.randint(80, 90)


def get_high_temp_copy():
    return str(get_high_temp()) + temp_unit


def get_low_temp():
    return random.randint(60, 70)


def get_low_temp_copy():
    return str(get_low_temp()) + temp_unit


if __name__ == "__main__":
    main()
