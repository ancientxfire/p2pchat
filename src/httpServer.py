from bottle import route, run
from constants import Config
from bottle import static_file
from constants import Config
import logging
logging.basicConfig(level=Config.loggingLevel, format=Config.loggingFormat)
logger = logging.getLogger("bottlepy")

def runHTTPServer(host,debug = False,quiet=True):
    @route('/publicCerts/<filename>')
    def server_static(filename):
        return static_file(filename, root=Config.httpServer.pathToPublicCerts)
    
    run(host=host, port=Config.httpServer.httpServerPort, debug=debug, quiet=quiet)
    
if __name__ == '__main__':
    runHTTPServer()