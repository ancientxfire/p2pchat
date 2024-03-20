import json
import logging
import sys
import socket


import struct
from zeroconf import Zeroconf

TYPE = "_pyChat._tcp.local."
NAME = '65486ads0IOJDasd-asdasdasd-asdasd'


def convDict(x):
    y = {}
 
    # Converting
    for key, value in x.items():
        y[key.decode("utf-8")] = value.decode("utf-8")
    return y
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    zeroconf = Zeroconf()

    try:
        service = zeroconf.get_service_info(TYPE, NAME + '.' + TYPE)
        
        print(convDict(service.properties)["roomID"])
        for i in service.addresses:
            print('.'.join(map(str, struct.unpack('BBBB',i))))
    finally:
        zeroconf.close()