import cv2 as cv
from time import sleep
from threading import Thread, Lock
from vision import Vision


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
    screenshot = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0
    debug = None

    # vision
    vision_like_icon = None
    vision_more_icon = None

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

        # initialize the Vision class
        self.vision_like_icon = Vision(
            "images/like_icon.jpg", cv.TM_CCOEFF_NORMED, debug
        )
        self.vision_more_icon = Vision(
            "images/more_icon.jpg", cv.TM_CCOEFF_NORMED, debug
        )

    def click_like_targets(self, like_targets):
        for like_target in like_targets:
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

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        if screenshot is None:
            self.like_targets = None
            self.more_targets = None
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
                if self.screenshot is None:
                    like_targets = []
                    more_targets = []
                else:
                    like_targets = self.vision_like_icon.find(
                        self.screenshot, 0.8, (0, 0, 255)
                    )
                    more_targets = self.vision_more_icon.find(
                        self.screenshot, 0.8, (255, 0, 255)
                    )
                    if self.debug:
                        cv.imshow("Matches", self.screenshot)

                print(
                    str(self.state)
                    + " like:"
                    + str(like_targets)
                    + " more:"
                    + str(more_targets)
                )

            if self.state == BotState.INITIALIZING:
                if like_targets:
                    self.state = BotState.SEARCHING

            elif self.state == BotState.SEARCHING:
                if like_targets:
                    self.click_like_targets(like_targets)
                    self.state = BotState.CLICKING

            elif self.state == BotState.CLICKING:
                if like_targets:
                    self.click_like_targets(like_targets)
                    self.state = BotState.CLICKING
                else:
                    self.state = BotState.SEARCHING

            self.lock.release()
