import asyncio
import json
import uuid
import websockets
import logging
from pymitter import EventEmitter
ee = EventEmitter()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


    

            
async def init_client(wsURL:str, headers: dict):
    logger.info("Starting websocket client")
    
    async for websocket in websockets.connect(uri=wsURL,logger=logger,extra_headers=headers):
        
        try:
            firstMessageStr = "Hi there!"
            firstMessage = {"uuid": headers["UUID"], "type":"init", "message":"Hi there!", "messageUUID":str(uuid.uuid5(uuid.NAMESPACE_DNS, firstMessageStr))} 
            print(json.dumps(firstMessage, indent=4))
            await websocket.send(json.dumps(firstMessage))
            
            @ee.on("send_message")
            async def send_message(msg):
                messageToSend = {"uuid": headers["UUID"], "type":"message", "message":msg, "messageUUID":str(uuid.uuid5(uuid.NAMESPACE_DNS, msg))}
                print(json.dumps(messageToSend))
                await websocket.send(json.dumps(messageToSend))
            
            while True:
                message = await websocket.recv()
                print(message)
        except websockets.ConnectionClosed:
            continue
        except Exception as e:
            logger.exception(e)
            
            

def startClient(wsURL, password, username):
    headers = {
        "Authorization": "Password: "+password,
        "Username": username,
        "UUID": str(uuid.uuid5(uuid.NAMESPACE_DNS, username))
    }
    try:
        # run init_client and test func simultaneouslly
        
        asyncio.run(init_client(wsURL=wsURL, headers=headers))
        run_client = asyncio.ensure_future(init_client(wsURL=wsURL, headers=headers))
        event_loop = asyncio.get_event_loop()
        event_loop.run_forever()
    except Exception as e:
        logger.exception(f"Exception in websocket server init: {e}")
    finally:
        run_client.cancel()
        event_loop.close()


if __name__ == "__main__":
    wsURL = "ws://localhost:8765"
    password= "mypass123"
    username = "ancie"
    startClient(wsURL=wsURL, password=password, username=username)