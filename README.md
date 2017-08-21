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

## How to use UDPGeolocate
Make sure that you've got Python 2.x installed on your OS, download this repository, and then run from the terminal with root privileges (using `sudo`, a root shell or similar mechanisms): `python /path/to/UDPGeolocate.py`

Make sure to replace the path with the correct path to the script.

## Config
### Minimum packet length
This is the minimum packet length (including things besides the payload, such as the header and IP information) which should trigger UDPGeolocate's querying mechanism. Setting it to low can cause rogue UDP packets to trigger false results with UDPGeolocate.

### UDP port
The port on which UDPGeolocate should listen on for packets. Can be detected by UDPGeolocate by running the video chat service with microphone and camera disabled. Stranger must have video enabled for detection to work. A skip or two shouldn't throw the detection off too much.

### Minimum timeout
The minimum amount of time that UDPGeolocate should take between checking on the IP address. Set to a higher value for less frequent checks, and for less strain on the CPU.

## Contributions
If anybody has access to a windows machine, then I would gladly welcome any contributions to make this script work on windows! I was thinking of maybe using `netsh trace` or WinDump instead of tcpdump, so those may be viable solutions to get the script to work on Windows too. Sadly, I don't have access to a Windows development environment.

For debugging, just set the logger level to logging.DEBUG in the script.

In case of bugs, please open up an issue in the issue tracker, or email me: <algb12.19@gmail.com>
