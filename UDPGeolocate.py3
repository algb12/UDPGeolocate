#!/usr/bin/env python

import subprocess
import json
import platform
import sys
import os
import time
import urllib.request, urllib.parse, urllib.error
import re
import signal
import atexit
import logging
import threading
import queue
import tkinter as tk

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
        # Directory wherein this file is contained
        self.CUR_DIR = os.path.dirname(os.path.realpath(__file__))
        self.running = True
        self.procs = []
        self.myQueue = queue.Queue()
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
                    urllib.request.urlretrieve(
                        self.WINDUMP_URL, self.CUR_DIR + "\WinDump.exe")
                except:
                    logging.error(
                        'Couldn\'t download WinDump into script directory. Please download manually.')
                    sys.exit(2)
            logging.info('Windows prerequisite check passed.')
        return 0

    # Detect UDP port used by service
    def detect_UDP_port(self, secs):
        # Probe for UDP packets and count number of packets per port
        attempts = 0
        ports = {}
        while attempts < self.PORT_PROBING_ATTEMPTS:
            if platform.system() == 'Darwin' or platform.system() == 'Linux':
                proc = subprocess.Popen(['sudo', 'tcpdump', '-n', '-c1', 'ip and udp and greater ' + str(
                    self.minPackLen)], stdout=subprocess.PIPE, stderr=self.NULL_DEVICE, stdin=subprocess.PIPE)
            if platform.system() == 'Windows':
                proc = subprocess.Popen([self.CUR_DIR + '\WinDump.exe', '-n', '-c1', 'ip and udp and greater ' + str(
                    self.minPackLen)], stdout=subprocess.PIPE, stderr=self.NULL_DEVICE, stdin=subprocess.PIPE)
            global procs
            self.procs.append(proc)
            output = proc.stdout.readline()
            logging.debug('Subprocess output returned: %s', output)
            proc.wait()
            self.procs.remove(proc)
            match = re.findall(
                r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]*', output.decode('utf-8'))[1].split('.')[4].strip()
            logging.debug('Match after regexes and split: %s', match)
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
    def get_IP_from_UDP_packet(self, port, minPackLen):
        if platform.system() == 'Darwin' or platform.system() == 'Linux':
            proc = subprocess.Popen(['sudo', 'tcpdump', '-n', '-c1', 'ip and udp src port ' + str(self.port) + ' and greater ' + str(
                self.minPackLen)], stdout=subprocess.PIPE, stderr=self.NULL_DEVICE, stdin=subprocess.PIPE)
        if platform.system() == 'Windows':
            proc = subprocess.Popen([self.CUR_DIR + '\WinDump.exe', '-n', '-c1', 'ip and udp src port ' + str(self.port) +
                                     ' and greater ' + str(self.minPackLen)], stdout=subprocess.PIPE, stderr=self.NULL_DEVICE, stdin=subprocess.PIPE)
        global procs
        self.procs.append(proc)
        output = proc.stdout.readline().strip()
        logging.debug('Subprocess output returned: %s', output)
        proc.wait()
        self.procs.remove(proc)
        if output:
            match = re.findall(
                r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', output.decode('utf-8'))[1].strip()
            logging.debug('Match after regexes: %s', match)
            return match
        return '0.0.0.0'

    # Function to get data for IP from geolocation API
    def get_IP_data(self, ip):
        url = self.GEOLOCATION_API_URL + ip
        handle = urllib.request.urlopen(url)
        jsonStr = handle.read().decode('utf-8')
        data = json.loads(jsonStr)
        logging.debug('Geolocation API (%s) returned data: %s', url, jsonStr)
        return data

    # Logic runs in a separate thread from GUI
    def logic_thread(self):
        logging.debug('Started logic thread')

        # Initially, set old IP to an arbitrary address
        oldIp = '0.0.0.0'

        # Loop to check for IP of UDP packet
        while self.running:
            # Don't do anything if IP is the same as old IP
            ip = self.get_IP_from_UDP_packet(self.port, self.minPackLen)
            if oldIp != ip:
                print(('Capturing UDP packet on port ' + str(self.port) + '...'))
                data = self.get_IP_data(ip)
                self.myQueue.put({'data': data, 'ip': ip})
            else:
                logging.debug('IP %s is identical to old IP', ip)
            oldIp = ip
            time.sleep(float(self.timeout))

    # Set config for UDPGeolocate
    def set_conf(self, minPackLen, port, timeout):
        self.minPackLen = minPackLen if minPackLen != '' else 200
        if port != '':
            self.port = port
        else:
            root = tk.Tk()
            root.title('Please wait')
            tk.Label(root, font=(None, 16),
                     text='Please wait while port is being detected...').pack()
            root.update_idletasks()
            root.update()
            self.port = u.detect_UDP_port(u.PORT_PROBING_ATTEMPTS)
            root.destroy()
        self.timeout = timeout if timeout != '' else 1

    # Gracefully stop subprocesses
    def stop_procs(self):
        for proc in self.procs:
            proc.terminate()
            proc.wait()
            logging.debug('Terminated process with PID %s', proc.pid)

    # Handler to gracefully exit app
    def stop_app(self):
        self.stop_procs()
        self.running = False


if __name__ == '__main__':
    print('### REAL-TIME UDP IP GEOLOCATOR ###')

    # Initiate main class
    u = UDPGeolocate()
    u.Windows_prereq_check()

    # Config dialogue
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", u.stop_app)

    root.title('Config')
    tk.Label(root, text='Minimum packet size').pack()
    minPackLenEntry = tk.Entry(root)
    minPackLenEntry.insert(0, 200)
    minPackLenEntry.pack()
    tk.Label(root, text='Port (leave blank for detection)').pack()
    portEntry = tk.Entry(root)
    portEntry.pack()
    tk.Label(root, text='Timeout (seconds)').pack()
    timeoutEntry = tk.Entry(root)
    timeoutEntry.insert(0, 1)
    timeoutEntry.pack()
    done_btn = tk.Button(root, text='Done', command=lambda: done_btn.config(state='disabled') or u.set_conf(
        minPackLenEntry.get(), portEntry.get(), timeoutEntry.get()) or root.destroy())
    done_btn.pack()

    root.mainloop()

    # Start logic thread
    t = threading.Thread(target=u.logic_thread)
    t.daemon = True
    t.start()

    # Initialise Tkinter
    root = tk.Tk()
    root.title('UDPGeolocate')

    # Initialise Tkinter vars
    labelsEntry = {}
    labelsValue = {}
    titleLabel = tk.Label(root, font=(
        None, 16), text='Geolocation data for UNDEFINED').grid(row=0, columnspan=2)
    tk.Button(root, text='Quit', command=u.stop_app).grid(row=1, columnspan=2)

    # Upon closing window, stop app
    root.protocol("WM_DELETE_WINDOW", u.stop_app)

    # GUI loop
    while u.running:
        try:
            elem = u.myQueue.get_nowait()
            data = elem['data']
            ip = elem['ip']
        except queue.Empty:
            # logging.debug('Queue empty')
            pass
        except KeyboardInterrupt:
            u.stop_app()
        else:
            logging.debug('Queue not empty')
            logging.debug(data)
            for widget in root.winfo_children():
                widget.destroy()
            titleLabel = tk.Label(root, font=(
                None, 16), text='Geolocation data for ' + str(ip)).grid(row=0)
            pos = 1
            for entry in data.keys():
                labelsEntry[entry] = tk.Label(
                    root, text=entry).grid(row=pos, stick='W')
                labelsValue[entry] = tk.Label(root, text=data[entry]).grid(
                    row=pos, column=1, stick='E')
                pos += 1
            tk.Button(root, text='Quit', command=u.stop_app).grid(
                row=pos, columnspan=2)
        try:
            root.update_idletasks()
            root.update()
        except tk.TclError:
            pass
