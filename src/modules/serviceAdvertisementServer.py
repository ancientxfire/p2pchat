import argparse
import random
import string
from time import sleep

from zeroconf import IPVersion, ServiceInfo, Zeroconf

from modules.argParsService import Arguments


def registerServiceAdvertisement(username,isPasswordProtected, roomID,ipAdress):
    
    args = Arguments().args



    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only
    
    desc = {'username': username,'roomID':roomID, "passwordProtected":isPasswordProtected}
    print("Registering service: "+roomID+"._pyChat._tcp.local.")
    info = ServiceInfo(
        "_pyChat._tcp.local.",
        roomID+"._pyChat._tcp.local.",
        addresses= [ipAdress],
        port=80,
        properties=desc,
        server="ash-2.local.",
    )

    zeroconf = Zeroconf(ip_version=ip_version)
    
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
