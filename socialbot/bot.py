import cv2 as cv
import pyautogui
from time import sleep
from vision import Vision
from windowcapture import WindowCapture


class InstaBot:
    # bot
    scroll_freq_secs = None
    other_freq_secs = None
    debug = None

    # state
    screenshot = None
    like_targets = None
    more_targets = None

    # window
    wincap = None
    window_offset = None

    # vision
    vision_like_icon = None
    vision_more_icon = None

    def __init__(self, scroll_freq_secs=1, other_freq_secs=2, debug=False):
        # set bot properties
        self.debug = debug
        self.scroll_freq_secs = scroll_freq_secs
        self.other_freq_secs = other_freq_secs

        # initialize the WindowCapture class
        self.wincap = WindowCapture("BlueStacks App Player")

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in
        # the whole object
        self.window_offset = (self.wincap.offset_x, self.wincap.offset_y)

        # set vision properties
        self.vision_like_icon = Vision(
            "images/instagram/like_icon.jpg", cv.TM_CCOEFF_NORMED, debug
        )
        self.vision_more_icon = Vision(
            "images/instagram/more_icon.jpg", cv.TM_CCOEFF_NORMED, debug
        )

        self.__calculate_state()

    def is_alive(self):
        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        key = cv.waitKey(1)
        if key == ord("q"):
            self.__set_screenshot(None)
            cv.destroyAllWindows()
            return False

        return True

    # state
    def has_like_targets(self):
        return self.like_targets

    def has_more_targets(self):
        return self.more_targets

    # actions
    def scroll_down(self):
        x, y = self.__get_click_position(self.__get_screen_midpoint())
        pyautogui.scroll(-1, x, y)
        print("action -> scroll down")
        sleep(self.scroll_freq_secs)

        self.__calculate_state()

    def scroll_up(self):
        x, y = self.__get_click_position(self.__get_screen_midpoint())
        pyautogui.scroll(1, x, y)
        print("action -> scroll up")
        sleep(self.scroll_freq_secs)

        self.__calculate_state()

    def click_like_targets(self):
        before_click = len(self.like_targets)
        for like_target in self.like_targets:
            screen_x, screen_y = self.__get_click_position(like_target)
            # pyautogui.moveTo(x=screen_x, y=screen_y)
            # pyautogui.click()
            print("click  -> x:{} y:{}".format(screen_x, screen_y))
            sleep(self.other_freq_secs)

        self.__calculate_state()
        return before_click - len(self.like_targets)

    def __calculate_state(self):
        while True:
            self.screenshot = self.wincap.get_screenshot()
            if self.screenshot is None:
                print("no screenshot, waiting for 1 sec...")
                sleep(1)
            else:
                break

        x, y = self.__get_click_position(self.__get_screen_midpoint())
        self.like_targets = self.vision_like_icon.find(
            self.screenshot,
            0.8,
            [0, x],
            None,
            (0, 0, 255),
            self.debug,
        )
        self.more_targets = self.vision_more_icon.find(
            self.screenshot, 0.8, None, None, (255, 0, 255), self.debug
        )

        if self.debug:
            cv.drawMarker(
                self.screenshot,
                self.__get_screen_midpoint(),
                (0, 255, 255),
                markerType=cv.MARKER_CROSS,
                markerSize=300,
                thickness=2,
            )
            cv.imshow("Matches", self.screenshot)

            print(
                "state  -> "
                + " like:"
                + str(self.like_targets)
                + " more:"
                + str(self.more_targets)
            )

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    def __get_click_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def __get_screen_midpoint(self):
        return (int(self.wincap.w / 2), int(self.wincap.h / 2))
