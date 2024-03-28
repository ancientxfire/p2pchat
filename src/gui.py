import asyncio
import logging
from commsTestwsClient import startClient
from pymitter import EventEmitter
ee = EventEmitter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




if __name__ == '__main__':
    wsURL = "ws://localhost:8765"
    password= "mypass123"
    username = "ancie"
    

        
    try:
        run_client = asyncio.ensure_future(asyncio.gather(startClient(wsURL=wsURL, password=password, username=username)))
        event_loop = asyncio.get_event_loop()
        event_loop.run_forever()
    except Exception as e:
        logger.exception(f"Exception in websocket server init: {e}")
    finally:
        run_client.cancel()
        event_loop.close()