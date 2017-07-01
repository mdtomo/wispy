#!/usr/bin/env python3

# Wispy v0.0.1

import sys
import subprocess
import pcapy
import time
import threading
import itertools
import struct

INTERFACE = ''
CHANNEL_HOP_DELAY = 5
SHUTDOWN = False

def main():
    if len(sys.argv) == 3:
        global CHANNEL_HOP_DELAY
        CHANNEL_HOP_DELAY = sys.argv[2]
    elif len(sys.argv) != 2:
        print('\nUsage: wispy.py <wlan-interface> <channel-hop-delay>\n')
        sys.exit(1)
    else:
        INTERFACE = sys.argv[1]
        if enable_monitor_mode(INTERFACE):
            print('OK')
            start_channel_hop()
            start_packet_capture()
        else:
            sys.exit(1)

def start_packet_capture():
    print('Packet capture starting on ' + INTERFACE)
    time.sleep(1)
    capture = pcapy.open_live(INTERFACE, 1514, 1, 10)
    capture.setfilter('subtype probe-req')
    while True:
        try:
            header_type = capture.datalink()
            (header, pkt) = capture.next()
            if header_type == 0x7F and len(pkt) > 0: # 0x7F/127 RadioTap header 
                packet_handler(header, pkt)    
        except KeyboardInterrupt:
            global SHUTDOWN
            SHUTDOWN = True
            disable_monitor_mode()
            break
     
def enable_monitor_mode(wifi_interface):
    try:
        global INTERFACE
        INTERFACE = wifi_interface
        print('Starting ' + INTERFACE + ' in monitor mode...', end= ' ')
        iw = subprocess.Popen(['iw', 'dev', INTERFACE, 'interface', 'add', INTERFACE + 'mon', 'type', 'monitor'])
        INTERFACE = wifi_interface + 'mon'
        ifconfig = subprocess.Popen(['ifconfig', INTERFACE, 'up'])
        return True
    except:
        return False
              
def disable_monitor_mode():
    print('Removing monitor interface...', end=' ')
    ifconfig = subprocess.Popen(['ifconfig', INTERFACE, 'down'])
    iw = subprocess.Popen(['iw', 'dev', INTERFACE, 'del'])
    print('OK')
    sys.exit(1)
       
def packet_handler(header, pkt):
    ts = header.getts()
    ms = '%06i' % int(ts[1])
    ts = time.strftime('%Y-%m-%d %H:%M:%S:', time.localtime(ts[0])) + str(ms)
    mac = struct.unpack_from('6s', pkt, 36)
    macstr = ':'.join(['%02x' % m for m in mac[0]])
    chan = struct.unpack_from('<H', pkt, 18)
    rssi = struct.unpack_from('<b', pkt, 22)
    ssidlen = pkt[51]
    print(str(ts) + ' MAC: %s CHAN: %s(%s) RSSI: %s SSID: ' % (macstr, chan[0], '%02i' % CHANNEL, rssi[0]), end=' ')
    if ssidlen > 0:
        ssid = pkt[52:52+ssidlen].decode('utf-8')
        print(ssid)
    else:
        print('<None>')   

def change_channel():
    global CHANNEL
    while True:
        if SHUTDOWN == False:
            subprocess.Popen(['iwconfig', INTERFACE, 'channel', str(CHANNEL)])
            CHANNEL = next(CHANNEL_ITERATOR)
            time.sleep(CHANNEL_HOP_DELAY)
        else:
            break

def start_channel_hop():
    channels = list(range(1, 12))
    global CHANNEL_ITERATOR
    CHANNEL_ITERATOR = itertools.cycle(channels)
    global CHANNEL
    CHANNEL = next(CHANNEL_ITERATOR)
    threading.Thread(target=change_channel).start()
    
if __name__ == '__main__':
    main()

    
