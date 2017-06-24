# Wispy
### Monitor 802.11 probe requests.

This project uses pcapy, a python wrapper for libpcap to capture 802.11 wifi probe requests. Probe requests are sent by Wifi clients while they are actively scanning for previously connected access points or looking for new access points. It is known that when clients are actively scanning for previously connected access points they will broadcast the name (SSID) of the access point in the probe request. This information can be of interest and provide an insight into the locations where the Wifi client has been connected before. Probe requests also provide a time stamp of when a client is physically in a local area.

Screenshot

### Prerequisites
* Python 3.4+
* A wireless interface capable of monitor mode. e.g. Alfa AWUS036H.
* 'iw' and 'ifconfig' for putting the interface into monitor mode and providing the channel hopping feature. Normally installed by default on most Linux installations.

## Installing
```
git clone https://github.com/mdtomo/wispy.git
./setup.py
```

## Example Usage
```
./wispy.py wlan0 10
Where 'wlan0' is the wifi interface capable of monitor mode. 
Where '10' is the delay in seconds between channel hopping. If omitted 5 seconds is the default delay.
```

## Future Features/Ideas
* Extra field for MAC vendor API lookup.
* Provide alert system for specific MACs when they become active/inactive. E.g email notify.
* Log results to a local SQLite db.
* Run as a daemon.
* Run a light weight local webserver to provide a frontend UI.

## Licence
This project is licensed under the MIT License - see the LICENSE.md file for details.
