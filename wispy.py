
# Wispy v0.0.2

import sys
import subprocess
import pcapy
import time
import threading
import itertools
import struct
import os
import requests
import config
import json
# Manually add path to virtual env because running under root uses the system installed python and not the ENV python.
sys.path.append(os.path.abspath('..') + '/lib/python3.6/site-packages') 
from manuf import manuf

INTERFACE = ''
CHANNEL_HOP_DELAY = 5
SHUTDOWN = False
MACPARSER = manuf.MacParser()

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
                if config.ENABLE_REMOTE_HOST:
                	send_data(parse_packet(header.getts(), pkt))
                else:
                	print(parse_packet(header.getts(), pkt))
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

       
def parse_packet(header, pkt):
    parsed_pkt = {}
   # parsed_pkt['ts'] = header[0]
   # parsed_pkt['tsms'] = '%06i' % header[1]
    parsed_pkt['ts'] = str(header[0]) + str('%06i' % header[1])
    parsed_pkt['mac'] = format_mac(struct.unpack_from('6s', pkt, 36))
    parsed_pkt['channel'] = '%i(%02i)' % (struct.unpack_from('<H', pkt, 18)[0], CHANNEL) 
    parsed_pkt['rssi'] = struct.unpack_from('<b', pkt, 22)[0]
    ssidlen = pkt[51]
    if ssidlen > 0:
        parsed_pkt['ssid'] = pkt[52:52+ssidlen].decode('utf-8')
    else:
        parsed_pkt['ssid'] = 'None'
    parsed_pkt['vendor'] = MACPARSER.get_comment(parsed_pkt['mac'])
    return parsed_pkt


def format_mac(macbytes):
    return ':'.join(['%02x' % m for m in macbytes[0]])


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


def send_data(data):
	try:	
                header = {'Authorization': 'Bearer ' + config.TOKEN}
                r = requests.post(config.PROBE_URL, headers=auth_header(config.TOKEN), json=data)
                print(str(r.status_code) + ' ' + r.reason + ' ' + r.text)
                if r.status_code == 401:
                    msg = r.json()
                    if msg['msg']  == 'Token has expired':
                        print('Requesting new access token.', end=' ')
                        r = requests.post(config.REFRESH_URL, headers=auth_header(config.REFRESH_TOKEN))
                        msg = r.json()
                        config.TOKEN = msg['access_token']
                        print('OK')
	except requests.exceptions.ConnectionError:
		print('Host is down.')


def auth_header(token):
    return {'Authorization': 'Bearer ' + token}

    
if __name__ == '__main__':
    main()

    
