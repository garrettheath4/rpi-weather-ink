#!/usr/bin/env python

import argparse

from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from font_intuitive import Intuitive
from inky import InkyPHAT, InkyWHAT

# phat-specific (as opposed to what-specific)
COLOR = "yellow"
scale_size = 1
padding = 0


def main():
    inky_display = InkyPHAT(COLOR)

    # inky_display.set_rotation(180)
    inky_display.set_border(inky_display.RED)

    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)

    #TODO: Draw background (white?)

    draw_text(str(get_uv()), inky_display.BLACK, 2, draw, inky_display.WIDTH)
    draw_text(str(get_cloudiness()), inky_display.BLACK, 3, draw, inky_display.WIDTH)
    draw_text(str(get_high_temp()), inky_display.BLACK, 1, draw, inky_display.WIDTH)
    draw_text(str(get_low_temp()), inky_display.BLACK, 4, draw, inky_display.WIDTH)


def draw_text(text, font_color, quadrant, draw, display_width):
    intuitive_font = ImageFont.truetype(Intuitive, int(22 * scale_size))
    hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(35 * scale_size))
    hanken_medium_font = ImageFont.truetype(HankenGroteskMedium, int(16 * scale_size))

    # UV Index
    uv_int = get_uv()
    uv_w, uv_h = hanken_medium_font.getsize(str(uv_int))
    uv_x = int((display_width - uv_w) / 2)
    uv_y = 0 + padding
    draw.text((uv_x, uv_y), str(uv_int), font_color, font=hanken_medium_font)


def get_uv():
    return 7


def get_cloudiness():
    return "Sunny"


def get_high_temp():
    return 85


def get_low_temp():
    return 65


if __name__ == "__main__":
    main()
