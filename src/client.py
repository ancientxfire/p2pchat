import time
from commsClient import runClientComms
from constants import Config
from modules.serviceAdvertisementServer import registerServiceAdvertisement
from modules.userChoice import userChoiceOne
from modules.zeroconfServices import getServerIpAndInfo
from resolver import askUserForRoom
import os

def runClient( forceRoomID: str = None,  username: str = "", ip:str = None,roomPassword: str =None):
    print("Client started")
    
    os.system("cls")
    roomData = None
    if forceRoomID != None:
        roomData = getServerIpAndInfo(forceRoomID)
    
    else:
        roomData = askUserForRoom()
    if roomData == None:
        print("Error: Room invalid")
        return 
    ips = roomData["IPs"]
    
    if ip == None and len(ips)> 1:
        ip, userIpID = userChoiceOne(ips,"Choose an IP adress. If not shure, choose the first one.")
    elif len(ips) == 1:
        ip = ips[0]
    wsURL = f"ws://{ip}:{Config.websocket.websocketPort}"
    isPasswordProtected = True
    if "properties" in roomData.keys() and 'passwordProtected' in roomData["properties"].keys():
        isPasswordProtected = bool(roomData["properties"]['passwordProtected'])
    if isPasswordProtected == False:
        roomPassword = ""
    elif roomPassword == None:
        roomPassword = input("Enter Password or press enter if no Password is set: ")
    
    if username == "":
        username = input("Username: ")
        
    runClientComms(wsURL=wsURL, password=roomPassword, username=username) 
    
if __name__ == "__main__":
    runClient()