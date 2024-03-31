import asyncio
import json
from queue import Queue
import ssl
import threading
import time
from websockets.sync.client import connect
import uuid
import logging

from chatGUI import runClientChatGUI
from constants import Config
logging.basicConfig(level=Config.loggingLevel, format=Config.loggingFormat)
logger = logging.getLogger("WS Client")

def messageReceive(websocket, extra_headers:dict,server_disconnected:threading.Event,messageQueue:Queue,newMessageRecivedEvent:threading.Event):
    try:
        for message in websocket:
            message = json.loads(message)
            
            
            match message["type"]:
                case "init":
                    print(message)
                case "message":
                    newMessageRecivedEvent.set()
                    messageQueue.put(message)
                    print(f"{message["sender"]}: {message["message"]}")
                case _:
                    print(message)


    except Exception as e:
        logger.exception(e)
    finally:
        server_disconnected.set()
        

def messageSendingLoop(websocket, extra_headers:dict, messageQueue:Queue,newMessageToSendEvent:threading.Event):
    try:
        welcomeMessageStr = "Hi Server"
        message = {"message": welcomeMessageStr, "messageUUID": str(uuid.uuid5(uuid.NAMESPACE_DNS, welcomeMessageStr)), "uuid": str(extra_headers["UUID"]), "type": "init"}
        websocket.send(json.dumps(message))
        while True:
            """ messageStr = input("Message: ") """
            newMessageToSendEvent.wait()
            messageStr = messageQueue.get()
            message = {"message": messageStr, "messageUUID": str(uuid.uuid5(uuid.NAMESPACE_DNS, messageStr)), "uuid": str(extra_headers["UUID"]), "type": "message"}
            websocket.send(json.dumps(message))
    except Exception as e:
        logger.exception(e)

def runClientComms(wsURL:str, password:str, username:str):

    extra_headers = {
            "Authorization": "Password: " + password,
            "Username": username,
            "UUID": str(uuid.uuid5(uuid.NAMESPACE_DNS, username))
    }
    with connect(wsURL, additional_headers=extra_headers) as websocket:
        server_disconnected = threading.Event()
        messageQueueRecived = Queue()
        newMessageRecivedEvent = threading.Event()
        messageQueueSend = Queue()
        newMessageToSendEvent = threading.Event()
        try:
            receive_thread = threading.Thread(target=messageReceive, args=[websocket, extra_headers, server_disconnected,messageQueueRecived, newMessageRecivedEvent])
            send_thread = threading.Thread(target=messageSendingLoop, args=[websocket, extra_headers,messageQueueSend, newMessageToSendEvent])
            receive_thread.daemon = True
            send_thread.daemon = True
            receive_thread.start()
            send_thread.start()
            
            runClientChatGUI(username,server_disconnected,messageQueueRecived,messageQueueSend, newMessageRecivedEvent,newMessageToSendEvent)
        except Exception as e:
            logger.exception(e)
        finally:
            logger.info("Exiting Client")

if __name__ == "__main__":
    wsURL = "ws://localhost:8765"
    password = input("Enter Password or press enter if no Password is set: ")
    username = input("Username: ")
    runClientComms(wsURL=wsURL, password=password, username=username)