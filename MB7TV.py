# MB7TV Image Tweeter by Nic M6XTN
# Will require the following python packages installed:
# tweepy, pywin32

# *** *** *** *** *** *** *** *** *** *** ***
# *** *** Configuration Items Go Here *** ***

# Directory to watch for new SSTV images:
watchDir = ""

# Template of tweeted image text can be changed here as desired
# [time] will be replaced with a date/time string:
messageTemplate = "MB7TV received at [time]"

# Format string for the time the file was created/image received:
timeFormat = "%Y-%m-%d %H:%M:%S UTC"

# Twitter API keys:
consumerKey = ""
consumerSecret = ""
accessToken = ""
accessTokenSecret = ""

# *** *** *** *** *** *** *** *** *** *** ***

import tweepy, os
import win32file, win32event, win32con
from datetime import datetime

# Set up tweepy
def twitterApi():
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)
    return api


# Image tweeter
def tweetImage(imagePath, text):
    api = twitterApi()
    api.update_with_media(imagePath, status=text)


# Get a directory change handler from OS
def getChangeHandle():
    handle = win32file.FindFirstChangeNotification(
        watchDir,
        0,
        win32con.FILE_NOTIFY_CHANGE_FILE_NAME)
    return handle


# Make sure watchDir is an absolute path
# and cd to watchDir
watchDir = os.path.abspath(watchDir)
os.chdir(watchDir)

print("Watching directory {}".format(watchDir))

changeHandle = getChangeHandle()

try:
    # Create a list of files already in the watched directory
    oldDirListing = dict([(f, None) for f in os.listdir(watchDir)])

    # Loop forever looking for file changes. Will time out
    # every so often allowing for keyboard interrupts to break the loop.
    while True:
        result = win32event.WaitForSingleObject(changeHandle, 500)

        # Check for a file notification event
        if result == win32con.WAIT_OBJECT_0:
            newDirListing = dict([(f, None) for f in os.listdir(watchDir)])

            # Create a list of new files against the old list
            added = [f for f in newDirListing if not f in oldDirListing]

            for f in added:
                # Check the file has a jpg or jpeg extension case insensitively
                if f.lower().endswith(('.jpg', '.jpeg')):

                    # Get file creation timestamp from OS
                    timeStamp = os.stat(f).st_ctime

                    # Convert posix timestamp to readable UTC datetime string
                    dateTime = datetime.utcfromtimestamp(timeStamp).strftime(timeFormat)

                    # Stitch together a message to accompany the image tweeted
                    message = messageTemplate.replace("[time]", dateTime)
                    print("\nTweeting: {} at {} with message: {}".format(f, dateTime, message))

                    # and tweet
                    tweetImage(f, message)

            # the new directory listing becomes the old directory listing
            oldDirListing = newDirListing
            win32file.FindNextChangeNotification(changeHandle)
finally:
    win32file.FindCloseChangeNotification(changeHandle)
