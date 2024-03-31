import asyncio
from http import HTTPStatus
import json
import ssl
from typing import Tuple
import uuid
import websockets
import logging

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

        





async def wsHandeler(websocket: websockets.WebSocketClientProtocol, path):
    global clientsNames
    wsUUID = ""
    isFirstMessage = True
    try:
        authorizedClients.add(websocket)
        print( clientsNames)
        while True:
            msg = await websocket.recv() 
            
            
            print(msg)
            if not "uuid"  in msg:
                errorMessage = {"errorType":"Malformed", "message":"Missing UUID parameter"}
                logger.error(errorMessage)
                await websocket.send(json.dumps(errorMessage))
            if not "messageUUID"  in msg:
                errorMessage = {"errorType":"Malformed", "message":"Missing messageUUID parameter"}
                logger.error(errorMessage)
                await websocket.send(json.dumps(errorMessage))
            if not "type"  in msg:
                errorMessage = {"errorType":"Malformed", "message":"Missing Type parameter"}
                logger.error(errorMessage)
                await websocket.send(json.dumps(errorMessage))
            else:
                
                msgDecoded = json.loads(msg)
                if isFirstMessage == False and msgDecoded["uuid"]!= wsUUID:
                    messageError = {"errorType":"Invalid UUID", "message":"UUID in message does't match previously send UUID"}
                    logger.error(errorMessage)
                    messageErrorStr = json.dumps(messageError)
                    await websocket.send(messageErrorStr)
                    break
                    
                elif isFirstMessage == True:
                    wsUUID = msgDecoded["uuid"]
                    logger.info("Recived init message from uuid: "+ wsUUID)
                    isFirstMessage = False
                    
                    if wsUUID not in clientsNames.values():
                        messageError = {"errorType":"Invalid UUID", "message":"UUID in message does't match any known UUID"}
                        messageErrorStr = json.dumps(messageError)
                        logger.error(errorMessage)
                        await websocket.send(messageErrorStr)
                        break
                    welcomeMessage = "Hello "+ [k for k, v in clientsNames.items() if v == wsUUID][0]
                    welcomeMessageDict =  {"type":"init", "message":welcomeMessage,"messageUUID" :str(uuid.uuid5(uuid.NAMESPACE_DNS, welcomeMessage))}
                    logger.info("Send Welcome Message: %s" %welcomeMessageDict)
                    await websocket.send(json.dumps(welcomeMessageDict))
                    print(wsUUID)
                
                if msgDecoded["type"] == "init":
                    continue
                
                if str(msgDecoded["messageUUID"]) != str(uuid.uuid5(uuid.NAMESPACE_DNS, msgDecoded["message"])):
                    messageError = {"errorType":"Invalid UUID", "message":"UUID does not macht message UUID"}
                    messageErrorStr = json.dumps(messageError)
                    logger.error(errorMessage)
                    logger.error(f"Message from UUID: {wsUUID}, was rejected because of invalid UUID")
                    await websocket.send(messageErrorStr)
                elif msgDecoded["type"] == "message":
                    logger.info(f"Broadcasting message from UUID: {wsUUID}")
                    for ws in authorizedClients:
                        if ws != websocket:
                            username = ""
                            keysClientsNames = [k for k, v in clientsNames.items() if v == wsUUID]
                            print(keysClientsNames)
                                    
                            message = {"uuid": msgDecoded["uuid"], "message": msgDecoded["message"], "sender":keysClientsNames[0], "type":"message"} 
                            messageStr = json.dumps(message)
                            await ws.send(messageStr)
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {websocket}")
    except Exception as e:
        logger.exception(f"Exception in websocket handler: {e}")
    finally:
        authorizedClients.remove(websocket)
        await websocket.close()
    




async def startWebSocketServer(password, wsAdressPort,wsAdress):
    global wsPassword
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