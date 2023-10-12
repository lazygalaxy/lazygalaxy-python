import cv2 as cv
import numpy as np
from threading import Thread, Lock
from time import sleep

class Detection:

    # threading properties
    stopped = True
    lock = None
    rectangles = []
    # properties
    screenshot = None
    needle_img = None
    threshold = None
    needle_w = 0
    needle_h = 0
    method = None

    def __init__(self, needle_img_path, threshold=0.6, method=cv.TM_CCOEFF_NORMED):
        # create a thread lock object
        self.lock = Lock()
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        # Save the dimensions of the needle image
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.threshold = threshold
        self.method = method


    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            if not self.screenshot is None:
                sleep(2)

                # lock the thread while updating the results
                self.lock.acquire()
                # run the OpenCV algorithm
                result = cv.matchTemplate(self.screenshot, self.needle_img, self.method)
                # print(result)
                # Get the all the positions from the match result that exceed our threshold
                locations = np.where(result >= self.threshold)
                locations = list(zip(*locations[::-1]))
                # print(locations)

                # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
                # locations by using groupRectangles().
                # First we need to create the list of [x, y, w, h] rectangles
                rectangles = []
                for loc in locations:
                    rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
                    # Add every box to the list twice in order to retain single (non-overlapping) boxes
                    rectangles.append(rect)
                    rectangles.append(rect)
                # Apply group rectangles.
                # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
                # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
                # in the result. I've set eps to 0.5, which is:
                # "Relative difference between sides of the rectangles to merge them into a group."
                rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

                self.rectangles = rectangles
                
                self.lock.release()
