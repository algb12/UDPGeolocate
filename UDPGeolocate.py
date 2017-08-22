import subprocess, json, platform, sys, os, time, urllib, re, logging

# Set logging level to logging.DEBUG for detailed debug info
logging.basicConfig(level=logging.INFO)

# Constants
GEOLOCATION_API_URL = 'http://ip-api.com/json/'
WINDUMP_URL = 'https://www.winpcap.org/windump/install/bin/windump_3_9_5/WinDump.exe'
PORT_PROBING_TIME = 5
NULL_DEVICE = open(os.devnull, 'wb')
# Directory wherein this file is contained
CUR_DIR = os.path.dirname(os.path.realpath(__file__))

# Windows prerequisites check
def Windows_prereq_check():
    if platform.system() == 'Windows':
        # Do we have WinPcap installed?
        if os.path.isfile('C:\\Windows\System32\wpcap.dll') == False:
            logging.error('WinPcap is not instaslled. Please install WinPcap.')
            sys.exit(1)
        # Is WinDump in the directory of this file?
        if os.path.isfile(CUR_DIR + '\WinDump.exe') == False:
            logging.warning('WinDump not found. Trying to download WinDump...')
            try:
                urllib.urlretrieve(WINDUMP_URL, CUR_DIR + "\WinDump.exe")
            except:
                logging.error('Couldn\'t download WinDump into script directory. Please download manually.')
                sys.exit(2)
        logging.info('Windows prerequisite check passed.')
        return 0
    else:
        return 0
    

# Detect UDP port used by service
def detect_UDP_port(secs):
    # Probe for UDP packets and count number of packets per port
    timeout = time.time() + secs
    ports = {}
    while time.time() < timeout:
        if platform.system() == 'Darwin' or platform.system() == 'Linux':
            proc = subprocess.Popen(['sudo', 'tcpdump', '-n', '-c1', 'ip and udp and greater ' + str(minPackLen)], stdout=subprocess.PIPE, stderr=NULL_DEVICE, stdin=subprocess.PIPE)
        if platform.system() == 'Windows':
            proc = subprocess.Popen([CUR_DIR + '\WinDump.exe', '-n', '-c1', 'ip and udp and greater ' + str(minPackLen)], stdout=subprocess.PIPE, stderr=NULL_DEVICE, stdin=subprocess.PIPE)
        output, err = proc.communicate()
        logging.debug('Subprocess output returned: %s', output)
        match = re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]*', output)[1].split('.')[4].strip()
        logging.debug('Match after regexes and split: %s', match)
        if match in ports:
            ports[match] += 1
        else:
            ports[match] = 1
        logging.debug('Port %s has %s occurrences', match, ports[match])
    # Calculate most common port
    lastPortCount = 0
    for curPort in ports:
        if ports[curPort] > lastPortCount:
            logging.debug('Port %s with %s occurrences is new candidate port', curPort, ports[curPort])
            port = curPort
            lastPortCount = ports[curPort]
    return port

# Function to extract IP from UDP packet
def get_IP_from_UDP_packet(port, minPackLen):
    if platform.system() == 'Darwin' or platform.system() == 'Linux':
        proc = subprocess.Popen(['sudo', 'tcpdump', '-n', '-c1', 'ip and udp src port ' + str(port) + ' and greater ' + str(minPackLen)], stdout=subprocess.PIPE, stderr=NULL_DEVICE, stdin=subprocess.PIPE)
    if platform.system() == 'Windows':
        proc = subprocess.Popen([CUR_DIR + '\WinDump.exe', '-n', '-c1', 'ip and udp src port ' + str(port) + ' and greater ' + str(minPackLen)], stdout=subprocess.PIPE, stderr=NULL_DEVICE, stdin=subprocess.PIPE)
    output, err = proc.communicate()
    logging.debug('Subprocess output returned: %s', output)
    match = re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', output)[1].strip()
    logging.debug('Match after regexes: %s', match)
    return match

# Function to get data for IP from geolocation API
def get_IP_data(ip):
    url = GEOLOCATION_API_URL + ip
    handle = urllib.urlopen(url)
    data = json.dumps(json.loads(handle.read()), indent=4, ensure_ascii=False).encode('utf8')
    logging.debug('Geolocation API (%s) returned data: %s', url, data)
    return data

if __name__ == '__main__':
    print '### REAL-TIME UDP IP GEOLOCATOR ###'

    Windows_prereq_check()

    # Request config input
    minPackLen = raw_input('Please enter the minimum packet size which should trigger a frame recording (Default: 200): ')
    port = raw_input('Please enter the UDP port number on which to listen for connections (Default: Detection by script (follow instructions later on in config!)): ')
    timeout = raw_input('Please enter the minimum timeout between each capture in seconds (Default: 1 second): ')

    # If no config input, set defaults
    if minPackLen == '':
        minPackLen = 200
    if port == '':
        raw_input('Please start the service, make sure that it\'s running, turn off the webcam and mic, and press enter to continue. After the port has been detected, re-enable the webcam and mic. The UDP packets will be probed for 5 seconds, and the most common destination port will be assumed as the one to use.')
        port = detect_UDP_port(int(PORT_PROBING_TIME))
    if timeout == '':
        timeout = 1

    # Initially, set old IP to an arbitrary address
    oldIp = '0.0.0.0'

    # Main loop to check for IP of UDP packet
    while True:
        try:
            # Don't do anything if IP is the same as old IP
            ip = get_IP_from_UDP_packet(port, minPackLen)
            if oldIp != ip:
                print 'Capturing UDP packet on port ' + str(port) + '...'
                print get_IP_data(ip)
                oldIp = ip
            else:
                logging.debug('IP %s is identical to old IP', ip)
            time.sleep(float(timeout))
        except KeyboardInterrupt:
            sys.exit()
