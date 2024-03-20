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

class MyListener(ServiceListener):
    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} added, service info: {info}")

def getAllServersInNetwork():



    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_pyChat._tcp.local.", listener)
    browser.cancel()
    try:
        input("Press enter to exit...\n\n")
    finally:
        zeroconf.close()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    print(getServerIpAndInfo("FVIO13"))