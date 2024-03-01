
# Could be useful to run queries easier in the program
def executeQuery(query, parameters):
    pass

def loginUser():
    pass

def registerUser():
    pass



response = ''
validResponse = False
while not validResponse:
    response = input("Would you like to login or register? ")
    if response.lower() == 'login' or response.lower() == 'register':
        validResponse = True
    else:
        print("Invalid response, type either 'login' or 'register'")


if response.lower() == 'login':
    loginUser()
elif response.lower() == 'register':
    registerUser()