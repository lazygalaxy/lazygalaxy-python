import cv2 as cv
import os
from bot import LikeBot

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize the like bot
bot = LikeBot(frequecy=2, debug=True)
bot.start()

while True:
    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    key = cv.waitKey(1)
    if key == ord("q"):
        bot.stop()
        cv.destroyAllWindows()
        break

print("Done.")
