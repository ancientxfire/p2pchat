import logging
class Config:
    # logging configuration
    loggingLevel = logging.INFO
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
    
    # crypto config
    class crypto:
        cert_file_server = '.\\src\\cryptoKeys\\server\\private\\certificate.pem'
        private_key_file_server = '.\\src\\cryptoKeys\\server\\private\\private_key.pem'
        public_key_file_server = '.\\src\\cryptoKeys\\server\\public\\public_key.pem'
        cert_file_client = '.\\src\\cryptoKeys\\client\\private\\certificate.pem'
        private_key_file_client = '.\\src\\cryptoKeys\\client\\private\\private_key.pem'
        public_key_file_client = '.\\src\\cryptoKeys\\client\\public\\public_key.pem'