import subprocess, json, platform, sys, os, time, urllib, re, logging

# Set logging level to logging.DEBUG for detailed debug info
logging.basicConfig(level=logging.INFO)

# Constants
GEOLOCATION_API_URL = 'http://ip-api.com/json/'
TOR_CHECK_URL = 'https://check.torproject.org/exit-addresses'
devnull = open(os.devnull, 'wb')

# Detect UDP port used by service
# NOTE: To be extended for Windows, maybe use netsh trace?
def detect_UDP_port(secs):
    # Probe for UDP packets and count number of packets per port
    timeout = time.time() + secs
    ports = {}
    while time.time() < timeout:
        if platform.system() == 'Darwin' or platform.system() == 'Linux':
            proc = subprocess.Popen(['sudo', 'tcpdump', '-n', '-c1', 'ip and udp and greater ' + str(minPackLen)], stdout=subprocess.PIPE, stderr=devnull, stdin=subprocess.PIPE)
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
# NOTE: To be extended for Windows, maybe use netsh trace?
def get_IP_from_UDP_packet(port, minPackLen):
    if platform.system() == 'Darwin' or platform.system() == 'Linux':
        proc = subprocess.Popen(['sudo', 'tcpdump', '-n', '-c1', 'ip and udp src port ' + str(port) + ' and greater ' + str(minPackLen)], stdout=subprocess.PIPE, stderr=devnull, stdin=subprocess.PIPE)
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

# Function to determine if IP is a Tor exit node
def IP_is_Tor_exit_node(ip):
    url = TOR_CHECK_URL
    handle = urllib.urlopen(url)
    data = handle.read()
    if ip in data:
        logging.debug('IP in Tor exit node list %s', url)
        return True
    else:
        logging.debug('IP not in Tor exit node list %s', url)
        return False

if __name__ == '__main__':
    print '### REAL-TIME UDP IP GEOLOCATOR ###'
    print '==================================='

    # Request config input
    minPackLen = raw_input('Please enter the minimum packet size which should trigger a frame recording (Default: 200): ')
    port = raw_input('Please enter the UDP port number on which to listen for connections (Default: Detection by script (follow instructions later on in config!)): ')
    timeout = raw_input('Please enter the minimum timeout between each capture in seconds (Default: 1 second): ')

    # If no config input, set defaults
    if minPackLen == '':
        minPackLen = 200
    if port == '':
        raw_input('Please start the service, make sure that it\'s running, turn off the webcam and mic, and press enter to continue. The UDP packets will be probed for 5 seconds, and the most common destination port will be assumed as the one to use.')
        port = detect_UDP_port(5)
    if timeout == '':
        timeout = 1

    # Initially, set old IP to an arbitrary address
    oldIp = '0.0.0.0'

    # Main loop to check for IP of UDP packet
    while True:
        try:
            # Don't do anything if IP is the same as old IP
            ip = get_IP_from_UDP_packet(port, minPackLen)
            if oldIp != ip and IP_is_Tor_exit_node(ip) == False:
                print 'Capturing UDP packet on port ' + str(port) + '...'
                print get_IP_data(ip)
                oldIp = ip
                time.sleep(float(timeout))
            else:
                logging.debug('IP %s in Tor exit node list or identical to old IP')
        except KeyboardInterrupt:
            sys.exit()
