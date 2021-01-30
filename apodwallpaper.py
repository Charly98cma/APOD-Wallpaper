#!/usr/bin/env python

from subprocess import run    as subRun
from requests   import get    as reqGet
from time       import sleep
from datetime   import datetime
from os.path    import isfile, getmtime, dirname, abspath


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
    print(" apodwallpaper.py -> apodPath - Checking if image need to be updated")
    res = 1
    if isfile(apodPath):
        # File exists
        lastModDay = datetime.utcfromtimestamp(getmtime(apodPath)).strftime("%Y/%m/%d")
        today = datetime.utcnow().strftime("%Y/%m/%d")
        if lastModDay == today:
            print(" apodwallpaper.py -> apodPath - Image up-to-date")
            res = 0
        else:
            # New APOD available => download
            print(" apodwallpaper.py -> apodPath - New image available")
    else:
        # File doesn't exists => download
        print(" apodwallpaper.py -> apodPath - No image found")
    return res


"""Function that check internet connectivity by pinging google.command

Return value (int)
------------------
0 - There's internet connectivity
1 - No internet connection

"""
def checkConn() -> int:
    print(" apodwallpaper.py -> checkConn - Checking internet connectivity")
    res = 0
    pingCount = 0
    # Check internet connectivity
    while pingCount < 5 and subRun(['ping', '-c1', 'google.com']).returncode != 0:
        pingCount += 1
        sleep(5)
    if pingCount == 5:
        res = 1
        print(" apodwallpaper.py -> checkConn - ERROR: No internet connectivity")
    return res



"""Function that gets the APOD url using the NASA API

Return value (str)
------------------
APOD URL - URL retrieved successfully
None     - Error

"""
def getAPOD() -> str:
    print(" apodwallpaper.py -> getAPOD - Downloading APOD image URL")
    photo = None
    # Used DEMO_KEY as the api_key since the constraints are based on IP
    response = reqGet('https://api.nasa.gov/planetary/apod',
                      params={
                          'api_key' : 'DEMO_KEY'
                      })
    # Status code check
    if response.status_code == 200:
        print(" apodwallpaper.py -> getAPOD - Download successful")
        photo = response.json()['hdurl']
    else:
        print(" apodwallpaper.py -> getAPOD - ERROR: Can't get the APOD image URL")
        print(" apodwallpaper.py -> getAPOD - ERROR CODE:", response.status_code)
    return photo



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
def downloadAPOD(apodURL, apodPath) -> int:
    print(" apodwallpaper.py -> downloadAPOD - Downloading APOD image")
    result = 0
    # Download APOD image
    response = reqGet(apodURL)
    if response.status_code == 200:
        print(" apodwallpaper.py -> downloadAPOD - Download successful")
        # Write new image (overwriting the older one)
        with open(apodPath, 'wb') as apodImage:
            apodImage.write(response.content)
            apodImage.truncate()
    else:
        # Error occurred => Print error messages
        result = 1
        print(" apodwallpaper.py -> downloadAPOD - ERROR: Download of APOD image failed")
        print(" apodwallpaper.py -> downloadAPOD - ERROR CODE:", response.status_code)
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
    print(" apodwallpaper.py -> setWallpaper - Running feh")
    # Run feh command using the photo local path
    res = subRun(
        ['feh', '--no-fehbg', '--bg-scale', apodPath]
    ).returncode
    # Check return code to print error message
    if res != 0:
        print(" apodwallpaper.py -> setWallpaper - ERROR: feh failed")
        print(" apodwallpaper.py -> setWallpaper - ERROR CODE:", res)
    return res



def main():
    print(" apodwallpaper.py -> main - Init script")
    # Path to APOD image on local storage
    apodPath = '/home/carlos/.dotfiles/.i3/wallpaper/APODWallpaper/apod-image.png'
    # Check if new APOD image available
    if checkAPOD(apodPath) == 1:
        if checkConn() == 1:
            exit(1)
        # Get APOD URL
        apodURL = getAPOD()
        if apodURL is None:
            exit(2)
            # Download image
        if downloadAPOD(apodURL, apodPath) == 1:
            exit(3)
    # Set APOD image
    setWallpaper(apodPath)
    exit(0)

if __name__ == "__main__":
    main()
