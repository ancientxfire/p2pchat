import random
import string
import time
from client import runClient
from modules.serviceAdvertisementServer import registerServiceAdvertisement
import multiprocessing

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
        roomID=''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        advertisementServer = multiprocessing.Process(target=registerServiceAdvertisement, args=["matthias", True,roomID])
        advertisementServer.start()
        subprocesses.append(advertisementServer)
        clientProc = multiprocessing.Process(target=runClient, args=[roomID])
        clientProc.start()
        subprocesses.append(clientProc)
        while True:
            time.sleep(1)
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