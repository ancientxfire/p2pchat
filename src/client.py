import time
from modules.serviceAdvertisementServer import registerServiceAdvertisement
from modules.zeroconfServices import getServerIpAndInfo
from resolver import askUserForRoom


def runClient( forceRoomID: str = None, roomPassword: str =None):
    print("Client started")
    roomData = None
    if forceRoomID != None:
        roomData = getServerIpAndInfo(forceRoomID)
        
    else:
        roomData = askUserForRoom()
    if roomData == None:
        print("Error: Room invalid")
        return 
    print(roomData)
    while True:
        time.sleep(1)
    
if __name__ == "__main__":
    runClient()