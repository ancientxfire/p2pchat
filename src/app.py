from client import runClient
from modules.serviceAdvertisementServer import *
from modules.userChoice import userChoiceOne
from resolver import askUserForRoom
from server import runServer

Arguments()

if __name__ == '__main__':
    args = Arguments().getArgs()
    if args.s == False and args.c == False:
        choice,choiceIndex = userChoiceOne(["Server","Client",])
        choice = "Server" if args.s else "Client" if args.c else choice
    else:
        choice = "Server" if args.s else "Client" if args.c else None
    if choice == "Server":
        runServer()
        
    elif choice == "Client":
        runClient()
    else:
        print("Wie bist du hier her gekommen?")
        exit(-1)