#!/usr/bin/env python
from subprocess import run       as subRun
from requests   import get       as reqGet
from time       import sleep
from datetime   import datetime
from os         import remove
from os.path    import isfile, getmtime, dirname, abspath, expanduser
from glob       import glob
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(filename)s - %(funcName)s - %(levelname)s: %(message)s',
    level=logging.INFO
)

"""Function that checks if there's a new APOD image available

Parameters
----------
apodPath : str - Path to the apod-image

Return value (int)
------------------
0 - The image is up-to-date
1 - New image available

"""
def checkAPOD(apodPath) -> int:
    logger.info("Checking if image need to be updated")
    res = 1
    if isfile(apodPath):
        # File exists
        lastModDay = datetime.utcfromtimestamp(getmtime(apodPath)).strftime("%Y/%m/%d")
        today = datetime.utcnow().strftime("%Y/%m/%d")
        if lastModDay == today:
            logger.info("Image up-to-date")
            res = 0
        else:
            # New APOD available => download
            logger.info("New image available")
    else:
        # File doesn't exists => download
        logger.info("No image found")
    return res


"""Function that check internet connectivity by pinging google.command

Return value (int)
------------------
0 - There's internet connectivity
1 - No internet connection

"""
def checkConn() -> int:
    logger.info("Checking internet connectivity")
    res = 0
    pingCount = 0
    # Check internet connectivity
    while pingCount < 5 and subRun(['ping', '-c1', 'google.com']).returncode != 0:
        pingCount += 1
        sleep(5)
    if pingCount == 5:
        res = 1
        logger.error("No internet connectivity")
    return res


"""Function that gets the APOD url using the NASA API

Return value (str)
------------------
APOD URL - URL retrieved successfully
None     - Error

"""
def getAPOD() -> str:
    logger.info("Downloading APOD image URL")
    # Used DEMO_KEY as the api_key since the constraints are based on IP
    response = reqGet('https://api.nasa.gov/planetary/apod',
                      params={
                          'api_key' : 'DEMO_KEY'
                      })
    # Status code check
    if response.status_code == 200:
        logger.info("Download successful")
        information = response.json()
        if information.get('media_type') == "image":
            url = response.json()['hdurl']
            isphoto = True
        elif information.get('media_type') == "video":
            url = response.json()['url']
            isphoto = False
        else:
            raise RuntimeError("APOD is not an image or video")
    else:
        logger.error("Can't get the APOD image URL")
        logger.error("Status code:", response.status_code)
    return (isphoto, url)


"""Function used to download the new APOD image, replacing the older one

Parameters
----------
apodURL  : str - URL of todays' APOd image
apodPath : str - Path to the apod-image on the users' computer

Return value (int)
------------------
0 - The new APOD image has been downloaded successfully
1 - Error

"""
def downloadAPOD(apodURL, apodPath, apodIsImage) -> int:
    logger.info("Downloading APOD image")
    result = 0
    # Download APOD image
    if apodIsImage:
        response = reqGet(apodURL)
        if response.status_code == 200:
            logger.info("Download successful")
            # Write new image (overwriting the older one)
            with open(apodPath, 'wb') as apodImage:
                apodImage.write(response.content)
                apodImage.truncate()
        else:
            # Error occurred => Print error messages
            result = 1
            logger.error("Download of APOD image failed")
            logger.error("Status code:", response.status_code)
    else:
        logger.info("Downloading APOD video")
        ytdl = subRun(['youtube-dl', apodURL, '-o', '/var/tmp/video'])
        if ytdl.returncode != 0:
            result = 1
            logger.error("Cannot download video with youtube-dl")
            logger.error(ytdl.stderr.decode())
        filename = glob("/var/tmp/video.*")[0]
        ffmpeg = subRun(["ffmpeg", "-y", "-i", filename, "-vcodec", "png", "-ss", "11", "-vframes", "1", "-an", "-f", "rawvideo", apodPathi])
        if ffmpeg.returncode != 0:
            result = 1
            logger.error("ffmpeg failed")
            logger.error({ffmpeg.returncode})
        remove(filename)
    return result


"""Function that sets the backgroud/wallpaper using feh

Parameters
----------
apodPath : str - Path to the apod-image.png on the users' computer

Return value (int)
------------------
0    - Image set successfully
None - Error

"""
def setWallpaper(apodPath) -> int:
    logger.info("Running feh")
    # Run feh command using the photo local path
    res = subRun(
        ['feh', '--no-fehbg', '--bg-scale', apodPath]
    ).returncode
    # Check return code to print error message
    if res != 0:
        logger.error("feh failed")
        logger.error("Status code:", res)
    return res



def main():
    logger.info("Init script")
    # Path to APOD image on local storage
    apodPath = expanduser("~/.wallpaper.png")
    # Check if new APOD image available
    if checkAPOD(apodPath) == 1:
        if checkConn() == 1:
            exit(1)
        # Get APOD URL
        apodIsImage, apodURL = getAPOD()
        if apodURL is None:
            exit(2)
        # Download image
        if downloadAPOD(apodURL, apodPath, apodIsImage) == 1:
            exit(3)

    # Set APOD image
    setWallpaper(apodPath)
    exit(0)

if __name__ == "__main__":
    main()

