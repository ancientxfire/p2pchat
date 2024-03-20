import json
import logging
import sys
import socket


import struct
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

TYPE = "_pyChat._tcp.local."



def convDict(x):
    y = {}
 
    # Converting
    for key, value in x.items():
        y[key.decode("utf-8")] = value.decode("utf-8")
    return y
def getServerIpAndInfo(searchRoomID):
    zeroconf = Zeroconf()

    try:
        service = zeroconf.get_service_info(TYPE, searchRoomID + '.' + TYPE)
        if service is None:
            return None
        propertys = service.properties
        ipAdresses = []
        for i in service.addresses:
            
            ipAdresses.append('.'.join(map(str, struct.unpack('BBBB',i))))
        return {"roomID":searchRoomID,"IPs":ipAdresses, "properties":convDict(propertys), }
    finally:
        zeroconf.close()

def getAllServersInNetwork():
    zeroconf = Zeroconf()

    try:
        servers = zeroconf.se
    finally:
        zeroconf.close()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    print(getServerIpAndInfo("FVIO13"))