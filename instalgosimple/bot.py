import cv2 as cv
import pyautogui
from time import sleep
from threading import Thread, Lock
from vision import Vision
from windowcapture import WindowCapture


class BotState:
    SCREEN_CAPTURING = 0
    IDLING = 1
    UP_SCROLLING = 2
    DOWN_SCROLLING = 3
    LIKE_CLICKING = 4


class LikeBot:
    # threading properties
    stopped = True
    lock = None

    # properties
    frequency = None
    debug = None
    wincap = None
    screenshot = None
    window_offset = None
    state = None

    # vision
    vision_like_icon = None
    vision_more_icon = None

    def __init__(self, frequecy=0.5, debug=False):
        # create a thread lock object
        self.lock = Lock()

        self.debug = debug
        self.frequency = frequecy

        # initialize the WindowCapture class
        self.wincap = WindowCapture("BlueStacks App Player")

        self.screenshot = self.wincap.get_screenshot()
        while self.screenshot is None:
            # wait until we get the first screenshot
            print("no screenshot, waiting for 1 sec...")
            sleep(1)
            self.screenshot = self.wincap.get_screenshot()

        if debug:
            cv.imshow("Matches", self.screenshot)

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in
        # the whole object
        self.window_offset = (self.wincap.offset_x, self.wincap.offset_y)

        self.state = BotState.SCREEN_CAPTURING

        # initialize the Vision class
        self.vision_like_icon = Vision(
            "images/like_icon.jpg", cv.TM_CCOEFF_NORMED, debug
        )
        self.vision_more_icon = Vision(
            "images/more_icon.jpg", cv.TM_CCOEFF_NORMED, debug
        )

    def click_like_targets(self, like_targets):
        self.state = BotState.IDLING
        for like_target in like_targets:
            if self.stopped:
                break

            self.state = BotState.LIKE_CLICKING
            screen_x, screen_y = self.get_click_position(like_target)
            # move the mouse
            # pyautogui.moveTo(x=screen_x, y=screen_y)
            # pyautogui.click()
            # print("clicked on x:{} y:{}".format(screen_x, screen_y))

    def down_scroll(self, clicks):
        self.state = BotState.DOWN_SCROLLING
        x, y = self.get_click_position(self.get_screen_midpoint())
        pyautogui.scroll(clicks, x, y)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the WindowCapture __init__ constructor.
    def get_click_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def get_screen_midpoint(self):
        return (int(self.wincap.w / 2), int(self.wincap.h / 2))

    # threading methods
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    # main logic controller
    def run(self):
        while not self.stopped:
            sleep(self.frequency)
            self.lock.acquire()

            self.screenshot = self.wincap.get_screenshot()

            if self.screenshot is None:
                like_targets = []
                more_targets = []
                self.state = BotState.SCREEN_CAPTURING
            else:
                like_targets = self.vision_like_icon.find(
                    self.screenshot, 0.8, (0, 0, 255)
                )
                more_targets = self.vision_more_icon.find(
                    self.screenshot, 0.8, (255, 0, 255)
                )
                if self.debug:
                    print(str(self.wincap.w) + " " + str(self.wincap.h))
                    cv.drawMarker(
                        self.screenshot,
                        self.get_screen_midpoint(),
                        (0, 255, 255),
                        markerType=cv.MARKER_CROSS,
                        markerSize=300,
                        thickness=2,
                    )
                    cv.imshow("Matches", self.screenshot)

            self.click_like_targets(like_targets)
            self.down_scroll(-3)

            print(
                str(self.state)
                + " like:"
                + str(like_targets)
                + " more:"
                + str(more_targets)
            )

            self.lock.release()
