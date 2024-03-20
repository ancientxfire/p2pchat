

import argparse
import json
import logging
import random
import socket
import string
from time import sleep
import uuid

from zeroconf import IPVersion, ServiceInfo, Zeroconf

EXCLUDED_IP_RANGES = ["172","100","127"]
def getAllIps():
    ip_addresses = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
    socket.gethostbyname_ex(socket.gethostname())
    conv_ip_addresses = []
    for adress in ip_addresses: 
        if adress.startswith(tuple(EXCLUDED_IP_RANGES)):
            continue
        conv_ip_addresses.append(socket.inet_aton(adress))
    return conv_ip_addresses
print(getAllIps())
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--v6', action='store_true')
    version_group.add_argument('--v6-only', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only
    roomID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    desc = {'username': 'matkop','roomID':roomID}

    info = ServiceInfo(
        "_pyChat._tcp.local.",
        "65486ads0IOJDasd-asdasdasd-asdasd._pyChat._tcp.local.",
        addresses= getAllIps(),
        port=80,
        properties=desc,
        server="ash-2.local.",
    )

    zeroconf = Zeroconf(ip_version=ip_version)
    print("Registration of a service, press Ctrl-C to exit...")
    zeroconf.register_service(info)
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()