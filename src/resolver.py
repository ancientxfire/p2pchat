import logging
import sys

from modules.userChoice import userChoiceOne
from modules.zeroconfServices import *
from modules.loadingAnimService import TermLoading


    

def askUserForRoom():
    
    animation: TermLoading = TermLoading()
    animation.show('searching...', finish_message='Finished!✅', failed_message='Failed!❌😨😨')
 
    allServers = getAllServersInNetwork()
    
    allServersResolved = []
    animation.finished = True
    if allServers != []:
        userOptions = []
        
        for itt, i in enumerate(allServers):
            info = getServerIpAndInfo(i["name"].replace("._pyChat._tcp.local.", ""))
            allServersResolved.append(info)
            userOptions.append(f"{chr(0x1F512) if info['properties']['passwordProtected'] else chr(0x1F513)} Room ID: {info['roomID']} IPs: {', '.join(info['IPs'])}")
        
        selectedRoomStr ,selectedIndex = userChoiceOne(userOptions,"Avalable Rooms:")
        return allServersResolved[selectedIndex]
    else:
        print("No Rooms available")
        return None

if __name__ == '__main__':
    print(askUserForRoom())