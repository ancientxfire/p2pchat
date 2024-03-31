import asyncio
from http import HTTPStatus
import json
import ssl
from typing import Tuple
import uuid
import websockets
import logging
import messageCrypto
from websockets.legacy.server import HTTPResponse
from constants import Config
logging.basicConfig(level=Config.loggingLevel, format=Config.loggingFormat)
logger = logging.getLogger("WS Server")



async def process_request( path: str, request_headers: websockets.Headers):
    global clientsNames,wsPassword

    try:
        print(path, request_headers)
        
        if not "authorization" in request_headers.keys():
            logger.info("REJECTED: No authorization header")
            return [HTTPStatus.BAD_REQUEST, {"Content-Type": "text/plain"}, b"Missing Authorization Header"]
        elif not "username" in request_headers.keys():
            logger.info("REJECTED: No username specified")
            return [HTTPStatus.BAD_REQUEST, {"Content-Type": "text/plain"}, b"Missing Username Header"]
        elif not "uuid" in request_headers.keys():
            logger.info("REJECTED: UUID missing")
            return [HTTPStatus.BAD_REQUEST, {"Content-Type": "text/plain"}, b"Missing UUID Header"]
        elif request_headers["Authorization"] != "Password: "+wsPassword and wsPassword != "":
            logger.info("REJECTED: Unauthorized")
            return [HTTPStatus.UNAUTHORIZED, {"Content-Type": "text/plain"}, b"Unauthorized"]
        elif str(uuid.uuid5(uuid.NAMESPACE_DNS, request_headers["username"]))!= request_headers["uuid"]:
            logger.info("REJECTED: Uuername and UUID do not match")
            return [HTTPStatus.NOT_ACCEPTABLE, {"Content-Type": "text/plain"}, b"UUID not valid"]
        elif request_headers["username"]  in clientsNames.keys() :
            if clientsNames[request_headers["username"]] == request_headers["uuid"]:
                logger.info("User Accepted: %s" % request_headers["username"])
                return None
            else:
                logger.info("REJECTED: Username already in use")
                return [HTTPStatus.NOT_ACCEPTABLE, {"Content-Type": "text/plain"}, b"Username is already taken"]
        
                  
            
            
            
            
        clientsNames[request_headers["username"]]=request_headers["uuid"]
        return None
    except Exception as e:
        logger.exception(f"Exception in processRequestHandeler: {e}")
        return [HTTPStatus.INTERNAL_SERVER_ERROR, {"Content-Type": "text/plain"}, b"Internal Server Error"]

        


async def sendMessage(websocket,messageJSON, wsUUID, type, encrypted = False):
    global clientsPublicKeys, server_private_key, server_public_key
    
    try:
        if encrypted == False:
            # send unencrypted message
            messageJSON["type"] = type
            messageWithWrapper = {"encrypted": encrypted, "message": messageJSON, "encrypted_message": ""}
            await websocket.send(json.dumps(messageWithWrapper))
            logger.info(f"Sent unencrypted {type} message to {wsUUID}")
        if encrypted == True:
            # send encrypted message
            messageJSON["type"] = type
            client_public_key = clientsPublicKeys[wsUUID]
            messageJSONStr = json.dumps(messageJSON)
            ciphertext = messageCrypto.encryptMessageWithPublicKey(messageJSONStr,client_public_key, )
            messageJSONWithWrapper = {"encrypted": True, "message": {}, "ciphertext": ciphertext, "signature":messageCrypto.signMessageWithPrivateKey(messageJSONStr,server_private_key)}

            
            await websocket.send(json.dumps(messageJSONWithWrapper))
            logger.info(f"Sent encrypted {type} message to {wsUUID}")
    except Exception as e:
        logger.exception(f"Exception in websocket message sender: {e}")


async def wsHandeler(websocket: websockets.WebSocketClientProtocol, path):
    global clientsNames, clientsPublicKeys, adminClients
    wsUUID = ""
    isFirstMessage = True
    try:
        authorizedClients.add(websocket)
        print( clientsNames)
        while True:
            msgWithWrapperStr = await websocket.recv()
            msgWithWrapper = json.loads(msgWithWrapperStr)
            print(msgWithWrapper)
            msgDecoded = msgWithWrapper["message"]
            encrypted = msgWithWrapper["encrypted"]
            
            
            if encrypted == True:
                ciphertext = msgWithWrapper["ciphertext"]
                client_public_key = clientsPublicKeys[wsUUID]
                cleartext = messageCrypto.msgDecript(ciphertext=ciphertext, private_key=server_private_key)
                isValid = messageCrypto.verifySignature(cleartext,client_public_key, msgWithWrapper["signature"])
                print(isValid)
                if isValid == False:
                    errorMessage = {"errorType":"Malformed", "message":"Invalid Signature"}
                    logger.error(errorMessage)
                    await sendMessage(websocket, errorMessage,wsUUID,"error")
                    continue
                msgDecoded = json.loads(cleartext)
            
            
            
            print(msgDecoded)
            if encrypted == False:
                if not "type"  in msgDecoded.keys():
                    errorMessage = {"errorType":"Malformed", "message":"Missing Type parameter"}
                    logger.error(errorMessage)
                    await sendMessage(websocket, errorMessage,wsUUID,"error")
                if not "uuid"  in msgDecoded.keys():
                    errorMessage = {"errorType":"Malformed", "message":"Missing UUID parameter"}
                    logger.error(errorMessage)
                    await sendMessage(websocket, errorMessage,wsUUID,"error")
                if not "messageUUID"  in msgDecoded.keys() and isFirstMessage == False:
                    errorMessage = {"errorType":"Malformed", "message":"Missing messageUUID parameter"}
                    logger.error(errorMessage)
                    await sendMessage(websocket, errorMessage,wsUUID,"error")

                else:
                    
                    
                    if isFirstMessage == False and msgDecoded["uuid"]!= wsUUID:
                        messageError = {"errorType":"Invalid UUID", "message":"UUID in message does't match previously send UUID"}
                        logger.error(errorMessage)
                        
                        await sendMessage(websocket, errorMessage,wsUUID,"error")
                        break
                    
                    elif isFirstMessage == True:
                        wsUUID = msgDecoded["uuid"]
                        logger.info("Recived init message from uuid: "+ wsUUID)
                        isFirstMessage = False
                        if not "public_key" in msgDecoded.keys():
                            errorMessage = {"errorType":"Malformed", "message":"Missing public_key parameter"}
                            logger.error(errorMessage)
                            await sendMessage(websocket, errorMessage,wsUUID,"error")
                        if wsUUID not in clientsNames.values():
                            messageError = {"errorType":"Invalid UUID", "message":"UUID in message does't match any known UUID"}
                            
                            logger.error(errorMessage)
                            await sendMessage(websocket, errorMessage,wsUUID,"error")
                            break
                        user_public_key_str=msgDecoded["public_key"]
                        user_public_key = messageCrypto.publicKeyFromString(user_public_key_str)
                        clientsPublicKeys[wsUUID] = user_public_key
                        server_public_key_str =  messageCrypto.publicKeyToString(server_public_key)
                        welcomeMessage = "Hello "+ [k for k, v in clientsNames.items() if v == wsUUID][0]
                        welcomeMessageDict =  { "message":welcomeMessage,"messageUUID" :str(uuid.uuid5(uuid.NAMESPACE_DNS, welcomeMessage)),"public_key":server_public_key_str}
                        logger.info("Client initialized with uuid:"+wsUUID)
                        await sendMessage(websocket, welcomeMessageDict,wsUUID,"init")
                        
                        
                    
                    match msgDecoded["type"]:
                        case "init":
                            continue
                        case "message":
                            # log end send error to client that only encrypted messages can be sent
                            logger.error(f"Message from UUID: {wsUUID}, was rejected because the message was send non encrypted ")
                            
                            await sendMessage(websocket, {"errorType":"Not Ecrypted", "message":"Message can only be send encrypted"},wsUUID,"error")
                        case "error":
                            error_message = msgDecoded["message"]
                            error_message["uuid"] = wsUUID
                            logger.error(error_message)
                            continue
                        case _:
                            logger.error(f"Message from UUID: {wsUUID}, was rejected because of invalid type")
                            await sendMessage(websocket, {"errorType":"Invalid Type", "message":"Invalid Type"},wsUUID,"error")
            elif encrypted == True:
                if not "type"  in msgDecoded.keys():
                    errorMessage = {"errorType":"Malformed", "message":"Missing Type parameter"}
                    logger.error(errorMessage)
                    await sendMessage(websocket, errorMessage,wsUUID,"error",True)
                elif not "uuid"  in msgDecoded.keys():
                    errorMessage = {"errorType":"Malformed", "message":"Missing UUID parameter"}
                    logger.error(errorMessage)
                    await sendMessage(websocket, errorMessage,wsUUID,"error",True)
                elif not "messageUUID"  in msgDecoded.keys() and msgDecoded["type"] == "message":
                    errorMessage = {"errorType":"Malformed", "message":"Missing messageUUID parameter"}
                    logger.error(errorMessage)
                    await sendMessage(websocket, errorMessage,wsUUID,"error",True)
                else:
                    match msgDecoded["type"]:
                        case "message":
                            if str(msgDecoded["messageUUID"]) != str(uuid.uuid5(uuid.NAMESPACE_DNS, msgDecoded["message"])):
                                messageError = {"errorType":"Invalid UUID", "message":"UUID does not macht message UUID"}
                                logger.error(f"Message from UUID: {wsUUID}, was rejected because of invalid UUID")
                                await sendMessage(websocket, messageError,wsUUID,"error",True)
                                continue
                            match msgDecoded["type"]:
                                case "message":
                                    logger.info(f"Broadcasting message from UUID: {wsUUID}")
                                    for ws in authorizedClients:
                                        if ws != websocket:
                                            username = ""
                                            keysClientsNames = [k for k, v in clientsNames.items() if v == wsUUID]
                                            print(keysClientsNames)

                                            message = {"uuid": msgDecoded["uuid"], "message": msgDecoded["message"], "sender":keysClientsNames[0], } 
                                            await sendMessage(ws, message,wsUUID,"message",True)
                                case _:
                                    logger.error(f"Message from UUID: {wsUUID}, was rejected because of invalid type")
                                    await sendMessage(websocket, {"errorType":"Invalid Type", "message":"Invalid Type"},wsUUID,"error", True)

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {websocket}")
    except Exception as e:
        logger.exception(f"Exception in websocket handler: {e}")
    finally:
        authorizedClients.remove(websocket)
        await websocket.close()
    




async def startWebSocketServer(password, wsAdressPort,wsAdress):
    global wsPassword
    global server_public_key,server_private_key
    server_private_key = messageCrypto.loadPrivateKey(Config.crypto.private_key_file_server)
    server_public_key = messageCrypto.loadPublicKey(Config.crypto.public_key_file_server)
    wsPassword = password

    
    logger.info("Starting websocket server")
    try:
        if wsAdress == None:
            wsAdress = "localhost"
       

        # start websocket server
        websocketServer = await websockets.serve(logger=logger, host=wsAdress, port=wsAdressPort,ws_handler=wsHandeler, process_request=process_request,)
        
        websocketServerTask = asyncio.ensure_future(websocketServer.serve_forever())

    except Exception as e:
        logger.exception(f"Exception in websocket server: {e}")

def runServerComms(password = "", wsAdressPort = Config.websocket.websocketPort,wsAdress = None):
    global authorizedClients
    global clientsNames
    global clientsPublicKeys
    global adminClients
    adminClients = {}
    clientsPublicKeys = {}
    wsAdress = str(wsAdress)
    clientsNames = {}
    authorizedClients = set()
    try:
        run_server = asyncio.ensure_future(startWebSocketServer(password=password,wsAdress=wsAdress,wsAdressPort=wsAdressPort))
        event_loop = asyncio.get_event_loop()
        event_loop.run_forever()
    except Exception as e:
        logger.exception(f"Exception in websocket server init: {e}")
    finally:
        run_server.cancel()
        
        event_loop.close()

if __name__ == "__main__":
    runServerComms(password="12345", wsAdress="localhost")