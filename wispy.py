#!/usr/bin/env python3

# WUDS - Wifi User Detection System, refactored.

import sys
import subprocess
import logging
import pcapy
import struct
import time
import radiotap


INTERFACE = ''

def main():
    if len(sys.argv) != 2:
        print('\nUsage: wuds.py <wlan-interface>\n')
        sys.exit(1)
    else:
        INTERFACE = sys.argv[1]
        if enable_monitor_mode(INTERFACE):
            start_packet_capture()
        else:
            sys.exit(1)
        #disable_monitor_mode()

def start_packet_capture():
    print('Packet capture starting on ' + INTERFACE)
    capture = pcapy.open_live(INTERFACE, 1514, 1, 0)
    capture.setfilter('subtype probe-req')
    while True:
        try:
            (header, pkt) = capture.next()
            if capture.datalink() == 0x7F: # 127
                packet_handler(header, pkt)
                #packet_handler2(pkt)
        except KeyboardInterrupt:
            disable_monitor_mode()
            break

        
def enable_monitor_mode(wifi_interface):
    #try:
        global INTERFACE
        INTERFACE = wifi_interface
        print('Starting ' + INTERFACE + ' in monitor mode.')
        #iw = subprocess.Popen(['ping', '127.0.0.1'], stdout=subprocess.PIPE)
        iw = subprocess.Popen(['iw', 'dev', INTERFACE, 'interface', 'add', INTERFACE + 'mon', 'type', 'monitor'], stdout=subprocess.PIPE)
        print(iw.communicate())
        INTERFACE = wifi_interface + 'mon'
        ifconfig = subprocess.Popen(['ifconfig', INTERFACE, 'up'], stdout=subprocess.PIPE)
        print(ifconfig.communicate())
        return True
    #except:
       # print('error stuff')
       # return False
        
    
        
def disable_monitor_mode():
    try:
        print('Removing monitor interface...', end=' ')
        ifconfig = subprocess.Popen(['ifconfig', INTERFACE, 'down'], stdout=subprocess.PIPE)
        iw = subprocess.Popen(['iw', 'dev', INTERFACE, 'del'])
        print('OK')
    except:
        print('error stuff')
        sys.exit(1)
        
 
def packet_handler(header, pkt):
    # print(str(datetime.now()) + 'Packet analysis \n')
    ts = header.getts()
    ts = time.strftime('%Y-%m-%d %H:%M:%S:', time.localtime(ts[0])) + str(ts[1])
    print(ts + ', Cap Size: %d, Pkt Size: %d' % (header.getcaplen(), header.getlen()))
    #print(dir(radiotap))
    print(pkt)
    print('Byte 51')
    print(pkt[51])
    (pktlen, parsedPkt) = radiotap.radiotap_parse(pkt)
    mac = radiotap.ieee80211_parse(pkt, pktlen)
    print(parsedPkt)
    print(mac)



def packet_handler2(pkt):
    print('pkt handler 2')
    # print(str(datetime.now()) + 'Packet analysis \n')
    rtlen = struct.unpack('h', pkt[2:4])[0]
    ftype = (pkt[rtlen] >> 2) & 3
    stype = pkt[rtlen] >> 4
    # check if probe request
    if ftype == 0 and stype == 4:
        rtap = pkt[:rtlen]
        frame = pkt[rtlen:]
        # parse bssid
        #bssid = frame[10:16].encode('hex')
        bssid = frame[10:16]
        bssid = ':'.join([bssid[x:x + 2] for x in range(0, len(bssid), 2)])
        # parse rssi
        rssi = struct.unpack('b', rtap[-6:-5])[0]  # there's another value at -3:-2 to investigate
        # parse essid
        essid = frame[26:26 + ord(frame[25])] if ord(frame[25]) > 0 else '<None>'
        # build data tuple
        data = (bssid, rssi, essid)
        print(data)

        
        
if __name__ == '__main__':
    main()
