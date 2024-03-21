import logging
import sys

from modules.zeroconfServices import *
from modules.loadingAnimService import TermLoading


    

def askUserForRoom():
    
    animation: TermLoading = TermLoading()
    animation.show('searching...', finish_message='Finished!✅', failed_message='Failed!❌😨😨')
 
    allServers = getAllServersInNetwork()
    
    allServersResolved = []
    animation.finished = True
    if allServers != []:
        print("Avalable Rooms:\n")
        for itt, i in enumerate(allServers):
            info = getServerIpAndInfo(i["name"].replace("._pyChat._tcp.local.", ""))
            allServersResolved.append(info)
            print(f"({itt}) {"🔒" if info["properties"]["passwordProtected"] else "🔓"} Room ID: {info["roomID"]} IPs: {", ".join(info["IPs"])}")
        
        selectedRoom = None
        
        while selectedRoom == None:
            try:
                inputedVal = int(input("Choose a Room: "))
                selectedRoom = allServersResolved[inputedVal]
            except ValueError:
                print("Please enter a valid number")
            
            except IndexError:
                print("Please enter a number shown above")
            except Exception as e:
                print(e)
        return selectedRoom
    else:
        print("No Rooms available")
        return None

if __name__ == '__main__':
    print(askUserForRoom())