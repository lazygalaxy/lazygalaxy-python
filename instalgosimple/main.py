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
wincap = WindowCapture("BlueStacks App Player")

# initialize the like bot
bot = LikeBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h), DEBUG)
bot.start()

# initialize the Vision class
vision_like_icon = Vision("images/like_icon.jpg", cv.TM_CCOEFF_NORMED, DEBUG)
vision_more_icon = Vision("images/more_icon.jpg", cv.TM_CCOEFF_NORMED, DEBUG)

while True:
    # get an updated image of the game
    screenshot = wincap.get_screenshot()

    # if we don't have a screenshot yet, don't run the code below this point yet
    # if screenshot is None:
    #     bot.update_targets(None)
    # else:
    # display the processed image
    like_targets = vision_like_icon.find(screenshot, 0.8, (0, 0, 255))
    more_targets = vision_more_icon.find(screenshot, 0.8, (255, 0, 255))
    #     bot.update_like_targets(like_targets)

    if DEBUG:
        cv.imshow("Matches", screenshot)

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    key = cv.waitKey(1)
    if key == ord("q"):
        bot.stop()
        cv.destroyAllWindows()
        break

print("Done.")
