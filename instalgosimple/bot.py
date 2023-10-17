import cv2 as cv
import pyautogui
from time import sleep, time
from threading import Thread, Lock
from math import sqrt


class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    CLICKING = 2


class LikeBot:
    # threading properties
    stopped = True
    lock = None

    # properties
    state = None
    like_targets = []
    more_targets = []
    screenshot = None
    movement_screenshot = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0
    debug = None

    def __init__(self, window_offset, window_size, debug=False):
        # create a thread lock object
        self.lock = Lock()

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in
        # the whole object
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        self.state = BotState.INITIALIZING
        self.debug = debug

    def click_like_targets(self):
        for like_target in self.like_targets:
            if self.stopped:
                break

            screen_x, screen_y = self.get_screen_position(like_target)
            # move the mouse
            # pyautogui.moveTo(x=screen_x, y=screen_y)
            # pyautogui.click()
            print("clicked on x:{} y:{}".format(screen_x, screen_y))

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the WindowCapture __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    # threading methods

    def update_like_targets(self, targets):
        self.lock.acquire()
        self.like_targets = targets
        self.lock.release()

    def update_more_targets(self, targets):
        self.lock.acquire()
        self.more_targets = targets
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    # main logic controller
    def run(self):
        while not self.stopped:
            sleep(1)
            self.lock.acquire()

            if self.debug:
                print(
                    str(self.state)
                    + " like:"
                    + str(self.like_targets)
                    + " more:"
                    + str(self.more_targets)
                )

            if self.state == BotState.INITIALIZING:
                if self.like_targets:
                    self.state = BotState.SEARCHING

            elif self.state == BotState.SEARCHING:
                if self.like_targets:
                    self.click_like_targets()
                    self.state = BotState.CLICKING

            elif self.state == BotState.CLICKING:
                if self.like_targets:
                    self.click_like_targets()
                    self.state = BotState.CLICKING
                else:
                    self.state = BotState.SEARCHING

            self.lock.release()
