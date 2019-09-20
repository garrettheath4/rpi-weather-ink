#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import random

from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from font_intuitive import Intuitive
from inky import InkyPHAT, InkyWHAT

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

    draw_text(get_uv(),             inky_display.BLACK, 2, img, display_size)
    draw_text(get_cloudiness(),     inky_display.BLACK, 3, img, display_size)
    draw_text(get_high_temp_copy(), inky_display.BLACK, 1, img, display_size)
    draw_text(get_low_temp_copy(),  inky_display.BLACK, 4, img, display_size)

    inky_display.set_image(img)
    inky_display.show()


def draw_text(text, font_color, quadrant, image, display_size):
    # intuitive_font = ImageFont.truetype(Intuitive, int(22 * scale_size))
    # hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(35 * scale_size))
    hanken_medium_font = ImageFont.truetype(HankenGroteskMedium, int(font_size * scale_size))

    # Ensure baselines line up by always calculating font height including cap
    # line height and descender line height (i.e. vertically align "ab" as if it
    # were as high as "Ay")
    _, font_height = hanken_medium_font.getsize("Ay")

    display_width, display_height = display_size

    text_str = text
    if type(text) not in (unicode, str):
        text_str = str(text)

    text_w, text_h = hanken_medium_font.getsize(text_str)
    text_x = int(max((display_width / 2) - text_w, 0) / 2)
    if quadrant in (1, 4):
        text_x += display_width / 2
    text_y = int(max((display_height / 2) - font_height, 0) / 2)
    if quadrant in (3, 4):
        text_y += display_height / 2

    ImageDraw.Draw(image).text((text_x, text_y), text_str, font_color, font=hanken_medium_font)


def get_uv():
    return random.randint(3, 9)


def get_cloudiness():
    # TODO: Draw a sun, cloud, or rain instead of words
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
