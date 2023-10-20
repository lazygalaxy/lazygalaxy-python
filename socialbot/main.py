import cv2 as cv
import os
from bot import InstaBot

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize the like bot
bot = InstaBot(scroll_frequency=0.5, other_frequecy=2, debug=True)

while True:
    if bot.has_like_targets():
        bot.click_like_targets()
    else:
        bot.scroll_down()

    bot.process_state()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    key = cv.waitKey(1)
    if key == ord("q"):
        cv.destroyAllWindows()
        break

print("Done.")
