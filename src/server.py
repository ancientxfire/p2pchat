import random
import string
import struct
import time
from client import runClient
from commsServer import runServerComms
from modules.serviceAdvertisementServer import registerServiceAdvertisement
import multiprocessing
from modules.ipServices import getAllIps
from modules.userChoice import userChoiceOne


def testFunc():
    i = 0
    while True:
        print(i)
        i += 1
        time.sleep(1)

def runServer():
    print("Server started")
    subprocesses = []
    try:
        # get password
        password = input("Room Password (Leave empty for no password): ")
        passwordProtected = True
        if password == "":
            password = None
            passwordProtected = False
        # get username
        username = input("Your Username: ")
        # user selected interface (ip)
        allIPs = getAllIps()
        allIPsConverted = []
        for ip in allIPs:
            allIPsConverted.append('.'.join(map(str, struct.unpack('BBBB',ip))))
        ip, userIpID = userChoiceOne(allIPsConverted,"Choose an IP adress. If not shure, choose the first one.")
        
        # start advertisement server in subprocess
        roomID=''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        advertisementServer = multiprocessing.Process(target=registerServiceAdvertisement, args=[username, passwordProtected,roomID, ip])
        advertisementServer.start()
        subprocesses.append(advertisementServer)
        # start client in subprocess
        
        serverProc = multiprocessing.Process(target=runServerComms, args=["" if password is None else password,8765,ip])
        serverProc.start()
        subprocesses.append(serverProc)
        # start websocket server in main process
        
        runClient(forceRoomID=roomID, username=username, roomPassword="" if password is None else password,ip=ip)
        
        
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt recived. Terminating...")
    except Exception as e:
        print(e)
    finally:
        for subproc in subprocesses:
            subproc.terminate()
            subproc.join()
        
if __name__ == "__main__":
    runServer()