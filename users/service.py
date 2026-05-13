import os

from PIL import ImageFont

from team_finder.constants import AVATAR_FONT_SIZE, FONT_PATHS


def get_font(size=AVATAR_FONT_SIZE):
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)
