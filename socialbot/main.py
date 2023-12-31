import cv2 as cv
import os
from bot import InstaBot

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

TOTAL_LIKES = 5
SCROLL_FREQ_SECS = 0.5
OTHER_FREQ_SECS = 2
DEBUG = True

# initialize the like bot
bot = InstaBot(SCROLL_FREQ_SECS, OTHER_FREQ_SECS, DEBUG)

likes = 0
while bot.is_alive() and likes < TOTAL_LIKES:
    if bot.has_more_text_targets():
        bot.click_more_text_targets()
    elif bot.has_like_icon_targets():
        likes += bot.click_like_icon_targets()
    else:
        bot.scroll_down()

print("Done.")
