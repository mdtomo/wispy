# Wispy
### Monitor 802.11 probe requests.

This project uses pcapy a python wrapper for libpcap to capture 802.11 wifi probe requests. Probe requests are sent by Wifi clients while they are actively scanning for previously connected access points or looking for new access points. It is known that when clients are actively scanning for previously connected access points they will include the name (SSID) of the access point in the probe request.

Requires a wireless interface capable of monitor mode. Tested on Raspian/Debian.

## Example Usage
```
./wispy.py wlan0 10
```

## 
