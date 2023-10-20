import cv2 as cv
import pyautogui
from time import sleep
from vision import Vision
from windowcapture import WindowCapture


class InstaBot:
    BAR_HEIGHT = 42

    # bot
    scroll_freq_secs = None
    other_freq_secs = None
    debug = None

    # state
    screenshot = None
    like_icon_targets = None
    more_icon_targets = None
    more_text_targets = None

    # window
    wincap = None
    window_offset = None

    # vision
    vision_like_icon = None
    vision_more_icon = None
    vision_more_text = None

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
        self.vision_more_text = Vision(
            "images/instagram/more_text.jpg", cv.TM_CCOEFF_NORMED, debug
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
    def has_like_icon_targets(self):
        return self.like_icon_targets

    def has_more_icon_targets(self):
        return self.more_icon_targets

    def has_more_text_targets(self):
        return self.more_text_targets

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

    def click_like_icon_targets(self):
        before_click = len(self.like_icon_targets)
        for like_target in self.like_icon_targets:
            screen_x, screen_y = self.__get_click_position(like_target)
            # pyautogui.moveTo(x=screen_x, y=screen_y)
            # pyautogui.click()
            print("click  -> like icon x:{} y:{}".format(screen_x, screen_y))
            sleep(self.other_freq_secs)

        self.__calculate_state()
        return before_click - len(self.like_icon_targets)

    def click_more_text_targets(self):
        before_click = len(self.more_text_targets)
        for more_text in self.more_text_targets:
            screen_x, screen_y = self.__get_click_position(more_text)
            pyautogui.moveTo(x=screen_x, y=screen_y)
            pyautogui.click()
            print("click  -> more text x:{} y:{}".format(screen_x, screen_y))
            sleep(self.other_freq_secs)

        self.__calculate_state()
        return before_click - len(self.more_text_targets)

    def __calculate_state(self):
        while True:
            self.screenshot = self.wincap.get_screenshot()
            if self.screenshot is None:
                print("no screenshot, waiting for 1 sec...")
                sleep(1)
            else:
                break

        x, y = self.__get_click_position(self.__get_screen_midpoint())
        self.like_icon_targets = self.vision_like_icon.find(
            self.screenshot,
            0.8,
            [0, x],
            None,
            (0, 0, 255),
            self.BAR_HEIGHT,
            self.debug,
        )

        self.more_icon_targets = self.vision_more_icon.find(
            self.screenshot, 0.8, None, None, (255, 0, 255), self.BAR_HEIGHT, self.debug
        )

        self.more_text_targets = self.vision_more_text.find(
            self.screenshot, 0.8, None, None, (255, 0, 255), self.BAR_HEIGHT, self.debug
        )

        if self.debug:
            if self.has_like_icon_targets() and self.has_more_icon_targets():
                # the image
                if (
                    self.more_icon_targets[0][1]
                    < self.like_icon_targets[len(self.like_icon_targets) - 1][1]
                ):
                    cv.rectangle(
                        self.screenshot,
                        self.more_icon_targets[0],
                        self.like_icon_targets[len(self.like_icon_targets) - 1],
                        (0, 255, 255),
                        2,
                    )

                point1 = (
                    self.like_icon_targets[0][0] - int(self.BAR_HEIGHT / 2),
                    self.like_icon_targets[0][1] + int(self.BAR_HEIGHT / 2),
                )
                point2 = (
                    self.more_icon_targets[len(self.more_icon_targets) - 1][0]
                    + int(self.BAR_HEIGHT / 2),
                    self.more_icon_targets[len(self.more_icon_targets) - 1][1]
                    - int(self.BAR_HEIGHT / 2),
                )
                # post comments
                if point1[1] < point2[1]:
                    cv.rectangle(
                        self.screenshot,
                        point1,
                        point2,
                        (0, 255, 255),
                        2,
                    )

            # draw the center marker
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
                + str(self.like_icon_targets)
                + " more:"
                + str(self.more_icon_targets)
            )

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    def __get_click_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def __get_screen_midpoint(self):
        return (int(self.wincap.w / 2), int(self.wincap.h / 2))
