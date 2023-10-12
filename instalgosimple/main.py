import cv2 as cv
import numpy as np
import os
from time import time
from windowcapture import WindowCapture
from vision import Vision
from bot import LikeBot

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

# initialize the WindowCapture class
wincap = WindowCapture('BlueStacks App Player')

# initialize the Vision class
vision_like_icon = Vision('images/like_icon.jpg', cv.TM_CCOEFF_NORMED, DEBUG)

# initialize the like bot
bot = LikeBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h), DEBUG)
bot.start()

while(True):
    # get an updated image of the game
    screenshot = wincap.get_screenshot()

    # if we don't have a screenshot yet, don't run the code below this point yet
    if screenshot is None:
        continue

    # display the processed image
    like_icon_points = vision_like_icon.find(screenshot, 0.9)
    bot.update_targets(like_icon_points)

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')
