#!/usr/bin/env python3

# Wispy v0.0.1

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
        print('\nUsage: wispy.py <wlan-interface>\n')
        sys.exit(1)
    else:
        INTERFACE = sys.argv[1]
        if enable_monitor_mode(INTERFACE):
            print('OK')
            start_packet_capture()
        else:
            sys.exit(1)
        #disable_monitor_mode()

def start_packet_capture():
    print('Packet capture starting on ' + INTERFACE)
    capture = pcapy.open_live(INTERFACE, 1514, 1, 1)
    capture.setfilter('subtype probe-req')
    while True:
        try:
            header_type = capture.datalink()
            (header, pkt) = capture.next()
            if header_type == 0x7F and len(pkt) > 0: # 127
                packet_handler(header, pkt)    
        except KeyboardInterrupt:
            disable_monitor_mode()
            break

        
def enable_monitor_mode(wifi_interface):
    #try:
        global INTERFACE
        INTERFACE = wifi_interface
        print('Starting ' + INTERFACE + ' in monitor mode...', end= ' ')
        iw = subprocess.Popen(['iw', 'dev', INTERFACE, 'interface', 'add', INTERFACE + 'mon', 'type', 'monitor'])
        INTERFACE = wifi_interface + 'mon'
        ifconfig = subprocess.Popen(['ifconfig', INTERFACE, 'up'])
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
    ts = header.getts()
    ts = time.strftime('%Y-%m-%d %H:%M:%S:', time.localtime(ts[0])) + str(ts[1])
    (pktlen, parsed_pkt) = radiotap.radiotap_parse(pkt)
    rtap_hdr = radiotap.ieee80211_parse(pkt, pktlen)
    #print(ts + ', Cap Size: %d, Pkt Size: %d' % (header.getcaplen(), header.getlen()))
    print(ts + ' MAC: %s CHAN: %d RSSI: %d SSID: ' % (rtap_hdr[1]['addr2'], parsed_pkt['chan_freq'], parsed_pkt['dbm_antsignal']), end=' ')
    ssidlen = pkt[51]
    if ssidlen > 0:
        ssid = pkt[52:52+ssidlen].decode('utf-8')
        print(ssid)
    else:
        print('<None>')   

def channel_hop(channel):
    iwconfig = subprocess.Popen(['iwconfig', INTERFACE, 'channel', channel])
        
if __name__ == '__main__':
    main()
