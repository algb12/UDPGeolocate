# UDPGeolocate
A geolocation script for Omegle, Chatroulette and the like

## What is UDPGeolocate?
UDPGeolocate is a script which runs in parallel to the video mode of random chat websites, such as Omegle and Chatroulette.

It allows one to find out information about the stranger, such as their location, IP address and ISP.

The script only works in video mode, as it relies on UDP packets, which are transmitted peer-to-peer, hence containing the IP address of the stranger.

What started out as a hacky Bash script for personal use, I have decided to turn into a more robust Python script and share it with the world to use!

## Why do we need this?
Basically, the answer is: it's a cool little thing. I am IN NO WAY for infiltrating the privacy of people, put considering that this information is public anyways, this script just makes it easier to make sense of this information.

Also, the country/city of the stranger may provide for some good conversation starter, so may other, more obscure information, such as their latitude and longitude.

Basically, use with care! I am NOT responsible or liable in any way for any direct or indirect damages incurred by this script, just saying!

## Prerequisites
### Installing Python 2.x (if applicable)
Make sure that you've got the latest Python 2.x installed on your OS. On OS X and Linux, this should be available out-of-the-box. If, for some strange reason, it isn't, it can be installed too. On Windows, however, it has to be installed. When installing Python on Windows, **make sure to enable the "Add to Path" option in the Python installer**!

Python can be downloaded from the [official Python website](https://www.python.org/).

### Installing WinPcap or Win10Pcap (Windows only)
For packet-layer network traffic access, and for WinDump to work, Windows needs the WinPcap drivers, which can be [downloaded here](https://www.winpcap.org/).

From Windows 10 onwards, due to a different Network Driver Interface Specification (NDIS), Win10Pcap has to be installed instead, which can be [downloaded here](http://www.win10pcap.org). WinDump will also work with Win10Pcap, according to [this source](https://www.coursehero.com/file/p79k3e2/Installing-Windump-Install-the-Windows-10-WinPcap-library-from/).

### Downloading UDPGeolocate
Obviously, this script has to be downloaded in order to be used. Simply download a .ZIP of this repository, extract it, and you're good to go!

### Downloading WinDump
As a tcpdump drop-in replacement, WinDump is the sniffer used by the script on Windows. The WinDump executable can be [downloaded here](https://www.winpcap.org/windump/), and should be placed in the same directory as the UDPGeolocate.py file resides in.

Normally, downloading WinDump is **not necessary**, because UDPGeolocate tries to download WinDump by itself if it is missing from its directory. If the download fails, however, UDPGeolocate will instruct the user to download WinDump and place it in the script directory at root level.

## Running UDPGeolocate
Make sure to replace the example path with the correct path to the script.
### OS X/Linux
Run from the terminal with root privileges (using `sudo`, a root shell or similar mechanisms): `python /path/to/UDPGeolocate.py`

### Windows
Run from the command line: `python.exe \path\to\UDPGeolocate.py`

In case the prerequisites check fails, follow the instructions printed out by UDPGeolocate.

## Config
### Minimum packet length
This is the minimum packet length (including things besides the payload, such as the header and IP information) which should trigger UDPGeolocate's querying mechanism. Setting it to low can cause rogue UDP packets to trigger false results with UDPGeolocate.

### UDP port
The port on which UDPGeolocate should listen on for packets. Can be detected by UDPGeolocate by running the video chat service with microphone and camera disabled. Stranger must have video enabled for detection to work. A skip or two shouldn't throw the detection off too much. After the port has been detected, you need to enable camera and microphone again for the geolocation to work properly.

### Minimum timeout
The minimum amount of time that UDPGeolocate should take between checking on the IP address. Set to a higher value for less frequent checks, and for less strain on the CPU.

## Contributions
For debugging, just set the logger level to logging.DEBUG in the script.

In case of bugs, please open up an issue in the issue tracker, or email me: <algb12.19@gmail.com>
