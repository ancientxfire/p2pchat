import logging
class Config:
    # logging configuration
    loggingLevel = logging.WARN
    loggingFormat = "%(name)s: %(asctime)s - %(levelname)s - %(message)s"


    
    class zeroconf:
        # zeroconf config
        zeroconfProtocol = "_pyChat._tcp.local."
    
    # websocket config
    
    class websocket:
        websocketPort = 8765
        
    # http server config
    
    class httpServer:
        
        httpServerPort = 8766
        pathToPublicCerts = ".\\src\\cryptoKeys\\server\\public"