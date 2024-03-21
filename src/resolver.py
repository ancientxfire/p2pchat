import logging
import sys

from services.zeroconfServices import *
from services.loadingAnimService import TermLoading


    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    print(getServerIpAndInfo("EECA9W"))
    animation: TermLoading = TermLoading()
    animation.show('searching...', finish_message='Finished!✅', failed_message='Failed!❌😨😨')
 
    allServers = getAllServersInNetwork()
    animation.finished = True
    print("allServers found:")
    for i in allServers:
        info = getServerIpAndInfo(i["name"].replace("._pyChat._tcp.local.", ""))
        print(f"Room ID: {info["roomID"]} IPs: {", ".join(info["IPs"])}")
       