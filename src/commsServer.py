import asyncio
from http import HTTPStatus
import json
from typing import Tuple
import uuid
import websockets
import logging

from websockets.legacy.server import HTTPResponse
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)






async def process_request( path: str, request_headers: websockets.Headers):
    global clientsNames
    
    try:
        print(path, request_headers)
        
        if not "authorization" in request_headers.keys():
            return [HTTPStatus.BAD_REQUEST, {"Content-Type": "text/plain"}, b"Missing Authorization Header"]
        elif not "username" in request_headers.keys():
            return [HTTPStatus.BAD_REQUEST, {"Content-Type": "text/plain"}, b"Missing Username Header"]
        elif not "uuid" in request_headers.keys():
            return [HTTPStatus.BAD_REQUEST, {"Content-Type": "text/plain"}, b"Missing UUID Header"]
        elif request_headers["Authorization"] != "Password: mypass123":
            return [HTTPStatus.UNAUTHORIZED, {"Content-Type": "text/plain"}, b"Unauthorized"]
        elif str(uuid.uuid5(uuid.NAMESPACE_DNS, request_headers["username"]))!= request_headers["uuid"]:
            
            return [HTTPStatus.NOT_ACCEPTABLE, {"Content-Type": "text/plain"}, b"UUID not valid"]
        elif request_headers["username"]  in clientsNames.keys() :
            if clientsNames[request_headers["username"]] == request_headers["uuid"]:
                return None
            else:
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
                await websocket.send(json.dumps(errorMessage))
            if not "messageUUID"  in msg:
                errorMessage = {"errorType":"Malformed", "message":"Missing messageUUID parameter"}
                await websocket.send(json.dumps(errorMessage))
            if not "type"  in msg:
                errorMessage = {"errorType":"Malformed", "message":"Missing Type parameter"}
                await websocket.send(json.dumps(errorMessage))
            else:
                
                msgDecoded = json.loads(msg)
                if isFirstMessage == False and msgDecoded["uuid"]!= wsUUID:
                    messageError = {"errorType":"Invalid UUID", "message":"UUID in message does't match previously send UUID"}
                    messageErrorStr = json.dumps(messageError)
                    await websocket.send(messageErrorStr)
                    break
                    
                elif isFirstMessage == True:
                    wsUUID = msgDecoded["uuid"]
                    isFirstMessage = False
                    
                    if wsUUID not in clientsNames.values():
                        messageError = {"errorType":"Invalid UUID", "message":"UUID in message does't match any known UUID"}
                        messageErrorStr = json.dumps(messageError)
                        await websocket.send(messageErrorStr)
                        break
                    print(wsUUID)
                
                if msgDecoded["type"] == "init":
                    continue
                
                if str(msgDecoded["messageUUID"]) != str(uuid.uuid5(uuid.NAMESPACE_DNS, msgDecoded["message"])):
                    messageError = {"errorType":"Invalid UUID", "message":"UUID does not macht message UUID"}
                    messageErrorStr = json.dumps(messageError)
                    logger.error(f"Message from UUID: {wsUUID}, was rejected because of invalid UUID")
                    await websocket.send(messageErrorStr)
                elif msgDecoded["type"] == "message":
                    
                    for ws in authorizedClients:
                        if ws != websocket:
                            username = ""
                            keysClientsNames = [k for k, v in clientsNames.items() if v == wsUUID]
                            print(keysClientsNames)
                                    
                            message = {"uuid": msgDecoded["uuid"], "message": msgDecoded["message"], "sender":keysClientsNames[0]} 
                            messageStr = json.dumps(message)
                            await ws.send(messageStr)
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {websocket}")
    except Exception as e:
        logger.exception(f"Exception in websocket handler: {e}")
    finally:
        authorizedClients.remove(websocket)
        await websocket.close()
    




async def startWebSocketServer():
    
    logger.info("Starting websocket server")
    try:
        wsAdress = "localhost"
        wsAdressPort = 8765
        
        websocketServer = await websockets.serve(logger=logger, host=wsAdress, port=wsAdressPort,ws_handler=wsHandeler, process_request=process_request,)
        
        websocketServerTask = asyncio.ensure_future(websocketServer.serve_forever())

    except Exception as e:
        logger.exception(f"Exception in websocket server: {e}")

if __name__ == "__main__":
    global authorizedClients
    global clientsNames
    clientsNames = {}
    authorizedClients:set = set()
    try:
        run_server = asyncio.ensure_future(startWebSocketServer())
        event_loop = asyncio.get_event_loop()
        event_loop.run_forever()
    except Exception as e:
        logger.exception(f"Exception in websocket server init: {e}")
    finally:
        run_server.cancel()
        
        event_loop.close()