def userChoiceOne(choices, question = "Choose one of the following: "):
    print(question)
    for itt, i in enumerate(choices):
        print(f"({itt}) {i}")
    choice = None
    choiceIndex = None
    while choice == None:
        try:
            userInp = int(input("Choice: "))
            choiceIndex = userInp
            choice = choices[choiceIndex]
        except ValueError:
            print("Please enter a number.")
        except IndexError:
            print("Please enter a valid number.")
    return choice, choiceIndex