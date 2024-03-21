def userChoiceOne(choices):
    print("choose one of the following: ")
    for itt, i in enumerate(choices):
        print(f"({itt}) {i}")
    choice = None
    while choice == None:
        try:
            userInp = int(input("Choice: "))
            choice = userInp
        except ValueError:
            print("Please enter a number.")
        except IndexError:
            print("Please enter a valid number.")
    return choice