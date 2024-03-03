import sqlite3

# GLOBAL VARIABLES
DB_PATH = '' # figure out later

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()



# Could be useful to run queries easier in the program
'''
A function to execute a query giving a query and set of parameters and return
the results as a list of tuples.
    query: a string which declares the query to be run
    parameters: a dict which maps the variables declared in the query string
    to the python variables intended

Example: simple login query
exampleQuery = 'SELECT * FROM members WHERE email=:loginEmail AND passwd=:loginPasswd'
exampleParameters = {'loginEmail': emailVar, 'loginPasswd': passwdVar}
executeQuery(exampleQuery, exampleParameters)
'''
def executeQuery(query: str, parameters: dict) -> list:
    c.execute(query, parameters)
    rows = c.fetchall()
    return rows

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




#conn.commit() # if you want to save changes to the db
conn.close()	

