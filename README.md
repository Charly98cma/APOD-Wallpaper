# APOD-Wallpaper
## Basic Info.
G'day!

This is a quite small Python script I've created using the NASA *Astronomy Picture Of the Day* ([APOD](https://apod.nasa.gov/apod/astropix.html)) API to set the APOD as your wallpaper/background image each time you run the script.

And, since we're all quite lazy, *systemd* will run the script on startup, after having internet connectivity, just follow the instructions down below.

## Dependencies

Well, you need [Python 3](https://www.python.org/), [pip](https://pypi.org/project/pip/), the program [feh](https://feh.finalrewind.org/) and the Python [requests](https://requests.readthedocs.io/en/master/) library.
To download a video, you'll also need [ffmpeg](https://ffmpeg.org/) and [youtube-dl](https://youtube-dl.org/)

To install the *requests* library, you can run the following command and *pip* will install it using the [requirements.txt](https://github.com/Charly98cma/APOD-Wallpaper/blob/main/requirements.txt) file.

``` bash
make init
```

The installation of *feh* is different depending on your distribution, but it's required to set the wallpaper/background image. If you use (or want to) a different program, I encourage you to open an [Issue](https://github.com/Charly98cma/APOD-Wallpaper/issues) and I'll add support for it, or, if you want to add it yourself, feel free to create a PR with your changes.

## Running script

To run the script manually, and change the wallpaper, you just have to run the next command:

``` bash
make run
```

Now, to run the script after the system boots, you'll have to follow a few but easy steps:
1. Run `make config`, to set the appropriate parameters on the *apodwallpaper.service* (absolute path of the Python script, in case you're wondering).
2. Now, to enable the *systemd* service, run the make command `make setup`, which does and runs the following (requires **sudo** permissions):
   1. Places the service file inside */etc/systemd/user* (requires **sudo**)
   1. Assign the appropriate permission to the service file by running `sudo chmod 644 /etc/systemd/user/apodwallpaper.service`. (requires **sudo**)
   3. Reload the systemd daemon by running `systemctl --user daemon-reload`
   2. Enable the service by running `systemctl --user enable apodwallpaper.service`

And that's all, from now on, after the system boots, the script will be executed, and the wallpaper will change.

## Credentials

I'm using the default **api_key** on the APOD requests, since the constraints to use it are based on the user IP, which is not a problem for this project, since each user will only download the image once each day.

But, if you want to use your own key, you can request one on the [NASA Open APIs](https://api.nasa.gov/) web.
