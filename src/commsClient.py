import asyncio
import json
from queue import Queue
import ssl
import threading
import time
from websockets.sync.client import connect
import uuid
import logging
import messageCrypto
from chatGUI import runClientChatGUI
from constants import Config
logging.basicConfig(level=Config.loggingLevel, format=Config.loggingFormat)
logger = logging.getLogger("WS Client")

def messageReceive(websocket, extra_headers:dict,server_disconnected:threading.Event,messageQueue:Queue,newMessageRecivedEvent:threading.Event):
    global server_public_key, shared_aes_key
    
    try:
        for messageWithWrapper in websocket:
            messageWithWrapper = json.loads(messageWithWrapper)
            
            msgDecoded = messageWithWrapper["message"]
            encrypted = messageWithWrapper["encrypted"]
            
            
            if encrypted == True:
                ciphertext = messageWithWrapper["ciphertext"]
                if messageWithWrapper["encryptionType"] == "rsa":
                    cleartext = messageCrypto.msgDecript(ciphertext=ciphertext, private_key=client_private_key)
                    isValid = messageCrypto.verifySignature(cleartext,server_public_key, messageWithWrapper["signature"])
                elif messageWithWrapper["encryptionType"] == "aes":
                    cleartext = messageCrypto.aesCrypto.decrypt(ciphertext,shared_aes_key)
                    isValid = True
                print(isValid)
                if isValid == False:
                    errorMessage = {"errorType":"Malformed", "message":"Invalid Signature recived by client","type":"error"}
                    logger.error(errorMessage)
                    sendWsMessage(websocket, errorMessage)
                    continue
                msgDecoded = json.loads(cleartext)
            message = msgDecoded
            match message["type"]:
                case "init":
                    print(message)
                    logger.info("Recived init message from server")
                    if not "public_key" in message:
                        logger.exception("No public key found in init message, aborting")
                        break
                    server_public_key = messageCrypto.publicKeyFromString(message["public_key"])
                    
                    # init aes
                    message = {"uuid": str(extra_headers["UUID"]), "type": "init_aes"}
                    print(message)
                    sendWsMessage(messageDict=message,webscoket=websocket,encrypted=True)
                    
                case "message":
                    newMessageRecivedEvent.set()
                    messageQueue.put(message)
                    print(f"{message["sender"]}: {message["message"]}")
                case "init_aes":
                    logger.info("init aes message was received")
                    if not "aesKey" in message.keys():
                        logger.exception("init aes message failed, not prrovided")
                        break
                    shared_aes_key = messageCrypto.base64Decode(message["aesKey"])
                    print(b"aaaa     "+shared_aes_key)
                case _:
                    print(message)


    except Exception as e:
        logger.exception(e)
    finally:
        server_disconnected.set()
        
def messageSendingLoop(websocket, extra_headers:dict, messageQueue:Queue,newMessageToSendEvent:threading.Event):
    global client_public_key
    try:
        welcomeMessageStr = "Hi Server"

        client_public_key_string = messageCrypto.publicKeyToString(client_public_key)
        message = {"message": welcomeMessageStr, "messageUUID": str(uuid.uuid5(uuid.NAMESPACE_DNS, welcomeMessageStr)), "uuid": str(extra_headers["UUID"]), "type": "init", "public_key":client_public_key_string}
        sendWsMessage(websocket, message)
        while True:
            """ messageStr = input("Message: ") """
            newMessageToSendEvent.wait()
            message = messageQueue.get()
            print(message)
            match message["type"]:
                case "message":
                    message = {"message": message["message"], "messageUUID": str(uuid.uuid5(uuid.NAMESPACE_DNS, message["message"])), "uuid": str(extra_headers["UUID"]), "type": "message"}
                    sendWsMessage(websocket, message, encrypted=True, encryptionType="aes")
                case "command":
                    
                    message = {"message": message["command"], "messageUUID": str(uuid.uuid5(uuid.NAMESPACE_DNS, json.dumps(message["command"]))), "uuid": str(extra_headers["UUID"]), "type": "command"}
                    sendWsMessage(websocket, message, encrypted=True, encryptionType="aes")

                case _:
                    logger.error("Invalid message type: %s", message["type"])

    except Exception as e:
        logger.exception(e)
def sendWsMessage(webscoket, messageDict:dict, encrypted = False, encryptionType = "rsa"):
    global server_public_key,client_private_key,shared_aes_key
    if encrypted == False:
        messageDictWithWrapper = {"encrypted": False, "message": messageDict}
        logger.info(messageDictWithWrapper)
        webscoket.send(json.dumps(messageDictWithWrapper))
    if encrypted == True:
        messageDictStr = json.dumps(messageDict)
        if encryptionType == "rsa":
            ciphertext = messageCrypto.encryptMessageWithPublicKey(messageDictStr,server_public_key, )
            messageDictWithWrapper = {"encrypted": True, "message": {}, "ciphertext": ciphertext, "signature":messageCrypto.signMessageWithPrivateKey(messageDictStr,client_private_key), "encryptionType":encryptionType}
            print(messageDictWithWrapper)
            logger.info(messageDictWithWrapper)
            webscoket.send(json.dumps(messageDictWithWrapper))
        elif encryptionType == "aes":
            print(b"bbbb     "+shared_aes_key)
            
            ciphertext = messageCrypto.aesCrypto.encrypt(messageDictStr, shared_aes_key)
            logger.info(ciphertext)
            messageDictWithWrapper = {"encrypted": True, "message": {}, "ciphertext": ciphertext, "signature":messageCrypto.signMessageWithPrivateKey(messageDictStr,client_private_key), "encryptionType":encryptionType}
            print(messageDictWithWrapper)
            logger.info(messageDictWithWrapper)
            webscoket.send(json.dumps(messageDictWithWrapper))
def runClientComms(wsURL:str, password:str, username:str):
    global client_public_key,client_private_key, shared_aes_key
    shared_aes_key = None
    #shared_aes_key = b'S2789l-d5kF-fUFu4Vj4P0dHtr5PBmnGmy6l0R9pQK0='
    client_private_key = messageCrypto.loadPrivateKey(Config.crypto.private_key_file_client)
    client_public_key = messageCrypto.loadPublicKey(Config.crypto.public_key_file_client)
    
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
            send_thread = threading.Thread(target=messageSendingLoop, args=(websocket, extra_headers,messageQueueSend, newMessageToSendEvent))
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