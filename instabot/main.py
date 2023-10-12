import cv2 as cv
import numpy as np
import os
from time import time
from windowcapture import WindowCapture
from detection import Detection
from vision import Vision
from bot import LikeBot, BotState

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their 
# own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

# initialize the WindowCapture class
wincap = WindowCapture('BlueStacks App Player')
# load the detector
like_icon_detector = Detection('images/like_icon.jpg')
# load an empty Vision class
vision = Vision()
# initialize the like bot
bot = LikeBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h), DEBUG)

wincap.start()
like_icon_detector.start()
bot.start()

while(True):

    # if we don't have a screenshot yet, don't run the code below this point yet
    if wincap.screenshot is None:
        continue

    # give detector the current screenshot to search for objects in
    like_icon_detector.update_screenshot(wincap.screenshot)
    targets = vision.get_click_points(like_icon_detector.rectangles)
    bot.update_targets(targets)
    
    if DEBUG:
        # draw the detection results onto the original image
        detection_image = vision.draw_rectangles(wincap.screenshot, like_icon_detector.rectangles)
        # display the images
        cv.imshow('Matches', detection_image)

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    key = cv.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        like_icon_detector.stop()
        bot.stop()
        cv.destroyAllWindows()
        break

print('Done.')
