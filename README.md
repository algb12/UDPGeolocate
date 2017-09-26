# UDPGeolocate
A geolocation script for Omegle, Chatroulette and the like

## What is UDPGeolocate?
UDPGeolocate is a script which runs in parallel to the video mode of random chat websites, such as Omegle and Chatroulette.

It allows one to find out information about the stranger, such as their location, IP address and ISP.

The script only works in video mode, as it relies on UDP packets, which are transmitted peer-to-peer, hence containing the IP address of the stranger.

UDPGeolocate started off as a hacky bash script (eww), and then became a command-line utility. Now it is a user-friendly GUI app!

## Why do we need this?
Basically, the answer is: It's a cool little thing. I am IN NO WAY for infiltrating the privacy of people, but considering that this information is public anyways, this script just makes it easier to make sense of this information.

Also, the country/city of the stranger may provide for some good conversation starter, so may other, more obscure information, such as their latitude and longitude.

Basically, use with care! I am NOT responsible or liable in any way for any direct or indirect damages incurred by this script, just saying!

## Prerequisites
### Installing Python (if applicable)
Make sure that you've got Python installed on your OS. On OS X and Linux, this should be available out-of-the-box. If, for some strange reason, it isn't, it can be installed too. On Windows, however, it has to be installed. When installing Python on Windows, **make sure to enable the "Add to Path" option in the Python installer**!

Python can be downloaded from the [official Python website](https://www.python.org/).

**IMPORTANT:** If you run UDPGeolocate with Python 3.x, use the file with the `.py3` extension. Use the one with the `py` extension for Python 2.x (version 2.6 or above).

### Installing WinPcap or Win10Pcap (Windows only)
For packet-layer network traffic access, and for WinDump to work, Windows needs the WinPcap drivers, which can be [downloaded here](https://www.winpcap.org/).

From Windows 10 onwards, due to a different Network Driver Interface Specification (NDIS), Win10Pcap has to be installed instead, which can be [downloaded here](http://www.win10pcap.org). WinDump will also work with Win10Pcap, according to [this source](https://www.coursehero.com/file/p79k3e2/Installing-Windump-Install-the-Windows-10-WinPcap-library-from/) and testing in a Windows 10 virtual machine.

### Installing Tcl/Tk (necessary on some Linux distributions)
If you use UDPGeolocate on Linux, then you may find that it doesn't run due to a lacking Tk/Tcl library. The installation process is different for every package manager.

On Ubuntu, for instance, to install Tcl/Tk for Python 2.x and 3.x using `apt-get`, run the following command:

`sudo apt-get install python-tk python3-tk`

### Installing Python3 on OS X/macOS (optional)
By default, OS X/macOS comes with Python 2.x (`python`), which needs no further adjustments for UDPGeolocate to run.

If, for whatever reason, you prefer Python 3.x (`python3`) on OS X/macOS instead, then install it from the [official Python website](https://www.python.org/).

### Downloading UDPGeolocate
Obviously, this script has to be downloaded in order to be used. Simply download a .ZIP of this repository, extract it, and you're good to go!

### Downloading WinDump (Windows only)
As a tcpdump drop-in replacement, WinDump is the sniffer used by the script on Windows. The WinDump executable can be [downloaded here](https://www.winpcap.org/windump/), and should be placed in the same directory as the UDPGeolocate.py file resides in.

Normally, downloading WinDump is **not necessary**, because UDPGeolocate tries to download WinDump by itself if it is missing from its directory. If the download fails, however, UDPGeolocate will instruct the user to download WinDump and place it in the script directory at root level.

## Running UDPGeolocate
Make sure to replace the example path with the correct path to the script.

### OS X/Linux
Run from the terminal, with root privileges: `sudo python /path/to/UDPGeolocate.py`

### Windows
Run from the command line: `python.exe \path\to\UDPGeolocate.py`

In case the prerequisites check fails, follow the instructions printed out by UDPGeolocate.

If you prefer to use Python 3.x instead, then replace `python` with `python3` instead.

## Config
### Minimum packet length
This is the minimum packet length (including things besides the payload, such as the header and IP information) which should trigger UDPGeolocate's querying mechanism. Setting it too low can cause rogue UDP packets to trigger false results with UDPGeolocate. Default: 200

### UDP port
The port on which UDPGeolocate should listen on for packets. Can be detected by UDPGeolocate simply by running detection mode along the video chat. A skip or two shouldn't throw the detection off too much, as UDPGeolocate samples 5 packets, and then uses the most common port. Default: detection by UDPGeolocate

### Minimum timeout
The minimum amount of time in seconds that UDPGeolocate should take between checking on the IP address. Set to a higher value for less frequent checks, and for less strain on the CPU. Default: 1

## Contributions
For debugging, just set the logger level to logging.DEBUG in the script on line 20. This will then output internal events of the script. They might not be interesting to the normal user, but if you feel like fiddling with the code or debugging if an error occurs, they can be quite helpful.

In case of bugs or suggestions, please open up an issue in the issue tracker, or email me: <algb12.19@gmail.com>
