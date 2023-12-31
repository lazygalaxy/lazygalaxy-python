import cv2 as cv
import numpy as np


class Vision:
    # properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None
    debug = None

    # constructor
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED, debug=False):
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        # Save the dimensions of the needle image
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method
        self.debug = debug

    def find(
        self,
        haystack_img,
        threshold=0.5,
        x_position=None,
        y_position=None,
        color=(255, 0, 255),
        size=20,
        debug=False,
    ):
        # run the OpenCV algorithm
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
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
        # print(rectangles)

        points = []
        if len(rectangles):
            marker_type = cv.MARKER_CROSS

            # Loop over all the rectangles
            for x, y, w, h in rectangles:
                # Determine the center position
                center_x = x + int(w / 2)
                center_y = y + int(h / 2)

                if (
                    x_position is None
                    or (x_position[0] <= center_x and center_x <= x_position[1])
                ) and (
                    y_position is None
                    or (y_position[0] <= center_y and center_y <= y_position[1])
                ):
                    # Save the points
                    points.append((center_x, center_y))

                    if self.debug:
                        # Draw the center point
                        cv.drawMarker(
                            haystack_img,
                            (center_x, center_y),
                            color,
                            markerType=marker_type,
                            markerSize=size,
                            thickness=2,
                        )

        return points
