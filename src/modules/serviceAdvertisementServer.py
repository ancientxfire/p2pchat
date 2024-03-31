import argparse
import random
import string
from time import sleep

from zeroconf import IPVersion, ServiceInfo, Zeroconf

from modules.argParsService import Arguments
import constants
import logging

logging.basicConfig(level=constants.Config.loggingLevel,format=constants.Config.loggingFormat)
logger = logging.getLogger("serviceAdvertisementServer")

def registerServiceAdvertisement(username,isPasswordProtected, roomID,ipAdress):
    
    args = Arguments().args



    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only
    zeroconfType = constants.Config.zeroconf.zeroconfProtocol
    desc = {'username': username,'roomID':roomID, "passwordProtected":isPasswordProtected}
    logger.info("Registering service: "+roomID+"."+zeroconfType)
    info = ServiceInfo(
        zeroconfType,
        roomID+"."+zeroconfType,
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
