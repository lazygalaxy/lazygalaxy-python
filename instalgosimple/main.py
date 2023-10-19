import cv2 as cv
import numpy as np
import os
from time import sleep
from windowcapture import WindowCapture
from bot import LikeBot

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

# initialize the WindowCapture class
wincap = WindowCapture("BlueStacks App Player")

screenshot = wincap.get_screenshot()
while screenshot is None:
    # wait until we get a screenshot
    print("no screenshot, waiting for 1 sec...")
    sleep(1)
    screenshot = wincap.get_screenshot()
if DEBUG:
    cv.imshow("Matches", screenshot)

# initialize the like bot
bot = LikeBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h), DEBUG)
bot.start()


while True:
    # if we don't have a screenshot yet, don't run the code below this point yet
    if screenshot is None:
        bot.update_screenshot(None)
    else:
        bot.update_screenshot(screenshot)

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    key = cv.waitKey(1)
    if key == ord("q"):
        bot.stop()
        cv.destroyAllWindows()
        break

    # get an updated image of the game
    screenshot = wincap.get_screenshot()

print("Done.")
