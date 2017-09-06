#!/usr/bin/env python

import subprocess
import json
import platform
import sys
import socket
import os
import time
import urllib
import re
import signal
import atexit
import logging
import threading
import Queue
import Tkinter as tk

# Set logging level to logging.DEBUG for detailed debug info
logging.basicConfig(level=logging.INFO)


class UDPGeolocate(object):
    """UDPGeolocate - A geolocation script for Chatroulette, Omegle and the like"""

    def __init__(self):
        super(UDPGeolocate, self).__init__()
        # Constants
        self.GEOLOCATION_API_URL = 'http://ip-api.com/json/'
        self.WINDUMP_URL = 'https://www.winpcap.org/windump/install/bin/windump_3_9_5/WinDump.exe'
        self.PORT_PROBING_ATTEMPTS = 5
        self.NULL_DEVICE = open(os.devnull, 'wb')
        self.CUR_DIR = os.path.dirname(os.path.realpath(__file__))
        self.HOST_IP = self.get_host_IP()
        # Initialise config attributes
        self.conf = {
            'min_pack_len': 200,
            'port': None,
            'timeout': 1
        }
        # Housekeeping and internal stuff
        self.running = True
        self.procs = []
        self.q = Queue.Queue()
        # Ensure graceful exit
        signal.signal(signal.SIGINT, signal.default_int_handler)
        atexit.register(self.stop_app)

    # Windows prerequisites check
    def Windows_prereq_check(self):
        if platform.system() == 'Windows':
            # Do we have WinPcap installed?
            if os.path.isfile('C:\\Windows\System32\wpcap.dll') == False:
                logging.error(
                    'WinPcap is not instaslled. Please install WinPcap.')
                sys.exit(1)
            # Is WinDump in the directory of this file?
            if os.path.isfile(self.CUR_DIR + '\WinDump.exe') == False:
                logging.warning(
                    'WinDump not found. Trying to download WinDump...')
                try:
                    urllib.urlretrieve(
                        self.WINDUMP_URL, self.CUR_DIR + "\WinDump.exe")
                except:
                    logging.error(
                        'Couldn\'t download WinDump into script directory. Please download manually.')
                    sys.exit(2)
            logging.info('Windows prerequisite check passed.')
        return 0

    # Detect UDP port used by service
    def detect_UDP_port(self, secs):
        logging.debug('Starting UDP port detection...')
        # Probe for UDP packets and count number of packets per port
        attempts = 0
        ports = {}
        while attempts < self.PORT_PROBING_ATTEMPTS:
            try:
                if platform.system() == 'Darwin' or platform.system() == 'Linux':
                    proc = subprocess.Popen(['sudo', 'tcpdump', '-n', '-c1', 'ip and udp and greater ' + str(
                        self.conf['min_pack_len'])], stdout=subprocess.PIPE, stderr=self.NULL_DEVICE, stdin=subprocess.PIPE)
                if platform.system() == 'Windows':
                    proc = subprocess.Popen([self.CUR_DIR + '\WinDump.exe', '-n', '-c1', 'ip and udp and greater ' + str(
                        self.conf['min_pack_len'])], stdout=subprocess.PIPE, stderr=self.NULL_DEVICE, stdin=subprocess.PIPE)
                self.procs.append(proc)
            except KeyboardInterrupt:
                sys.exit()
            output = proc.stdout.readline()
            logging.debug('Subprocess output returned: %s', output)
            proc.wait()
            self.procs.remove(proc)
            matches = re.findall(
                r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]*', output.decode('utf-8'))
            for tempMatch in matches:
                if self.HOST_IP in tempMatch:
                    match = tempMatch.split('.')[4].strip()
            logging.debug('Match after regex, IP filter and split: %s', match)
            if match in ports:
                ports[match] += 1
            else:
                ports[match] = 1
            attempts += 1
            logging.debug('Port %s has %s occurrences', match, ports[match])
        # Calculate most common port
        lastPortCount = 0
        for curPort in ports:
            if ports[curPort] > lastPortCount:
                logging.debug(
                    'Port %s with %s occurrences is new candidate port', curPort, ports[curPort])
                port = curPort
                lastPortCount = ports[curPort]
        return port

    # Function to extract IP from UDP packet
    def get_IP_from_UDP_packet(self, port, min_pack_len):
        try:
            if platform.system() == 'Darwin' or platform.system() == 'Linux':
                proc = subprocess.Popen(['sudo', 'tcpdump', '-n', '-c1', 'ip and udp port ' + str(self.conf['port']) + ' and greater ' + str(
                    self.conf['min_pack_len'])], stdout=subprocess.PIPE, stderr=self.NULL_DEVICE, stdin=subprocess.PIPE)
            if platform.system() == 'Windows':
                proc = subprocess.Popen([self.CUR_DIR + '\WinDump.exe', '-n', '-c1', 'ip and udp port ' + str(self.conf['port']) +
                                         ' and greater ' + str(self.conf['min_pack_len'])], stdout=subprocess.PIPE, stderr=self.NULL_DEVICE, stdin=subprocess.PIPE)
            self.procs.append(proc)
        except KeyboardInterrupt:
            sys.exit()
        output = proc.stdout.readline().strip()
        logging.debug('Subprocess output returned: %s', output)
        proc.wait()
        self.procs.remove(proc)
        if output:
            matches = re.findall(
                r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', output.decode('utf-8'))
            for match in matches:
                if self.HOST_IP not in match:
                    return match.strip()
            logging.debug('Match after regex and IP filter: %s', match)
        return '0.0.0.0'

    # Function to get data for IP from geolocation API
    def get_IP_data(self, IP):
        url = self.GEOLOCATION_API_URL + IP
        handle = urllib.urlopen(url)
        jsonStr = handle.read().decode('utf-8')
        data = json.loads(jsonStr)
        logging.debug('Geolocation API (%s) returned data: %s', url, jsonStr)
        return data

    def get_host_IP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        host_IP = s.getsockname()[0]
        logging.debug('Host IP is %s', host_IP)
        s.close()
        return host_IP

    # Logic runs in a separate thread from GUI
    def logic_thread(self):
        logging.debug('Started logic thread')

        # Initially, set old IP to an arbitrary address
        old_IP = '0.0.0.0'

        # Loop to check for IP of UDP packet
        while self.running:
            # Don't do anything if IP is the same as old IP
            IP = self.get_IP_from_UDP_packet(
                self.conf['port'], self.conf['min_pack_len'])
            if old_IP != IP:
                logging.debug('Capturing UDP packet on port ' +
                              str(self.conf['port']) + '...')
                data = self.get_IP_data(IP)
                self.q.put({'data': data, 'IP': IP})
            else:
                logging.debug('IP %s is identical to old IP', IP)
            old_IP = IP
            time.sleep(float(self.conf['timeout']))

    # Function to start the logic thread
    def start_logic_thread(self):
        # Start logic thread
        t = threading.Thread(target=self.logic_thread)
        t.daemon = True
        t.start()

    # Set config for UDPGeolocate
    def set_conf(self, min_pack_len, port, timeout):
        self.conf['min_pack_len'] = min_pack_len if min_pack_len.isdigit() and (
            int(min_pack_len) >= 0) else 200
        if port.isdigit() and (0 <= int(port) <= 65535):
            self.conf['port'] = port
        else:
            root = tk.Tk()
            root.title('Please wait')
            tk.Label(root, font=(None, 16),
                     text='Please wait while port is being detected...').pack()
            root.update_idletasks()
            root.update()
            try:
                self.conf['port'] = self.detect_UDP_port(
                    self.PORT_PROBING_ATTEMPTS)
            except KeyboardInterrupt:
                sys.exit()
            root.destroy()
        self.conf['timeout'] = timeout if timeout.isdigit() and (
            0 <= int(timeout) <= 10) else 1
        logging.debug('Config values: %s', self.conf)

    # Gracefully stop subprocesses
    def stop_procs(self):
        for proc in self.procs:
            try:
                proc.terminate()
                proc.wait()
                logging.debug(
                    'Successfully terminated process with PID %s', proc.pid)
            except:
                logging.debug(
                    'Error terminating process with PID %s', proc.pid)
                pass

    # Handler to gracefully exit app
    def stop_app(self):
        logging.debug('Exit handler invoked')
        self.stop_procs()
        self.running = False

    # Config dialogue
    def show_conf_dialogue(self):
        root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", sys.exit)

        root.title('Config')
        tk.Label(root, text='Minimum packet length').pack()
        root.min_pack_len_entry = tk.Entry(root)
        root.min_pack_len_entry.insert(0, 200)
        root.min_pack_len_entry.pack()
        tk.Label(root, text='Port (leave blank for detection)').pack()
        root.port_entry = tk.Entry(root)
        root.port_entry.pack()
        tk.Label(root, text='Timeout (seconds)').pack()
        root.timeout_entry = tk.Entry(root)
        root.timeout_entry.insert(0, 1)
        root.timeout_entry.pack()
        root.done_btn = tk.Button(root, text='Done')
        root.done_btn.config(command=lambda: self.on_conf_OK(root))
        root.done_btn.pack()

        root.mainloop()

    def on_conf_OK(self, root):
        root.done_btn.config(state='disabled')
        self.set_conf(root.min_pack_len_entry.get(),
                      root.port_entry.get(), root.timeout_entry.get())
        root.destroy()

    def update_GUI(self):
        try:
            elem = self.q.get_nowait()
            data = elem['data']
            IP = elem['IP']
        except Queue.Empty:
            # logging.debug('Queue empty')
            pass
        except KeyboardInterrupt:
            sys.exit()
        else:
            logging.debug('Queue not empty')
            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.title_label = tk.Label(self.root, font=(
                None, 16), text='Geolocation data for ' + str(IP) + ' (port ' + str(self.conf['port']) + '):').grid(row=0)
            pos = 1
            for entry in data.iterkeys():
                self.root.labels_entry[entry] = tk.Label(
                    self.root, text=entry).grid(row=pos, stick='W')
                self.root.labels_value[entry] = tk.Label(self.root, text=data[entry]).grid(
                    row=pos, column=1, stick='E')
                pos += 1
            tk.Button(self.root, text='Quit', command=sys.exit).grid(
                row=pos, columnspan=2)
        self.root.after(100, self.update_GUI)

    def show_main_GUI(self):
        self.root = tk.Tk()
        self.root.title('UDPGeolocate')

        # Initialise Tkinter vars
        self.root.labels_entry = {}
        self.root.labels_value = {}
        self.root.title_label = tk.Label(self.root, font=(
            None, 16), text='Awaiting new IP...').grid(row=0, columnspan=2)
        tk.Button(self.root, text='Quit', command=sys.exit).grid(
            row=1, columnspan=2)

        # Upon closing window, stop app
        self.root.protocol("WM_DELETE_WINDOW", sys.exit)

        # Tkinter GUI loop
        self.root.after(100, self.update_GUI)
        self.root.mainloop()


if __name__ == '__main__':
    # Initiate main class
    u = UDPGeolocate()

    # Check for the needed prerequisites on Windows
    u.Windows_prereq_check()

    # Show the UDPGeolocate config dialogue
    u.show_conf_dialogue()

    # Start the logic thread
    u.start_logic_thread()

    # Show main GUI
    u.show_main_GUI()
