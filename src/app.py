import os
from client import runClient
from modules.genCertChain import deleteCertChainForServerAndClient, generateCertChainForServerAndClient
from modules.serviceAdvertisementServer import *
from modules.userChoice import userChoiceOne
from resolver import askUserForRoom
from server import runServer
from constants import Config


if __name__ == '__main__':
    try:
      
        
        # register cmd arguments and parse them
        Arguments()
        args = Arguments().getArgs()
        if args.s == False and args.c == False:
            choice,choiceIndex = userChoiceOne(["Server","Client","Generate CertChain","Delete CertChain","CLOSE"])
            choice = "Server" if args.s else "Client" if args.c else choice
        else:
            choice = "Server" if args.s else "Client" if args.c else None
        if choice == "Server":
            allFilesPresent = []
            allFilesPresent.append(os.path.exists(Config.crypto.private_key_file_server))
            allFilesPresent.append(os.path.exists(Config.crypto.public_key_file_server) )
            allFilesPresent.append(os.path.exists(Config.crypto.cert_file_server))
            allFilesPresent.append(os.path.exists(Config.crypto.private_key_file_client))
            allFilesPresent.append(os.path.exists(Config.crypto.public_key_file_client) )
            allFilesPresent.append(os.path.exists(Config.crypto.cert_file_client))
            if not False in allFilesPresent:
                runServer()
            else:
                print("Generate the certificates and keyfiles first. [Gernerate CertChain] [Server + Client]")
            
        elif choice == "Client":
            allFilesPresent = []
            allFilesPresent.append(os.path.exists(Config.crypto.private_key_file_client))
            allFilesPresent.append(os.path.exists(Config.crypto.public_key_file_client) )
            allFilesPresent.append(os.path.exists(Config.crypto.cert_file_client))
            if not False in allFilesPresent:
                runClient()
            else:
                print("Generate the certificates and keyfiles first. [Gernerate CertChain] [Client]")
            
        elif choice == "Generate CertChain":
            generateCertChainForServerAndClient()
        elif choice == "Delete CertChain":
            deleteCertChainForServerAndClient()
        elif choice == "CLOSE":
            exit(0)
        else:
            print("Wie bist du hier her gekommen?")
            exit(-1)
    except Exception as e:
        print("Error", e)
        
    finally:
        exit(0)