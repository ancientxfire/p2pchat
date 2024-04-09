def parseCommand(origStr:str, commandInitiator = "/"):
    if len(origStr) < 2 :
        return {"isCommand": False}
    origStr = origStr.split()
    if origStr[0].startswith(commandInitiator) == False:
        return {"isCommand": False}
    if len(origStr) > 1:
        return {"isCommand": True, "command":origStr[0][1:], "params":origStr[1:]}
    else:
        return {"isCommand": True, "command":origStr[0][1:], "params": []}


if __name__ == "__main__":
    print(parseCommand("\\hallo matze"))