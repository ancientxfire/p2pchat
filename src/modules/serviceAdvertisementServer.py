import argparse
import random
import string
from time import sleep

from zeroconf import IPVersion, ServiceInfo, Zeroconf

from modules.argParsService import Arguments
from modules.ipServices import getAllIps


def registerServiceAdvertisement(username,isPasswordProtected):
    
    args = Arguments().args



    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only
    roomID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    desc = {'username': username,'roomID':roomID, "passwordProtected":isPasswordProtected}
    print("Registering service: "+roomID+"._pyChat._tcp.local.")
    info = ServiceInfo(
        "_pyChat._tcp.local.",
        roomID+"._pyChat._tcp.local.",
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
