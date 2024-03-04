import sqlite3
import sys

# GLOBAL VARIABLES
if len(sys.argv) != 2:
    print("Usage: python3 main.py <database_name>")
    sys.exit(1)
DB_NAME = sys.argv[1]
DB_PATH = f'{DB_NAME}.db'

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
def executeQuery(query: str, parameters: dict=None) -> list:
    if not parameters:
        c.execute(query)
    else:
        c.execute(query, parameters)
    rows = c.fetchall()    
    return rows

'''
Function to get members where given username and password matches the email in database,

Inputs: none
Returns: none
'''
def loginUser():
    emailVar = input("Enter your email: ")
    passwordVar = input("Enter your password: ")

    login_query = 'SELECT * FROM members WHERE email=? AND passwd=?'
    login_parameters = (emailVar, passwordVar)
    
    user = executeQuery(login_query, login_parameters)

    if user:
        print(f"Mogging awaits, {user[0][1]}!")
    else:
        print("Invalid email or password. Please try again.")
    
def registerUser():
    name = input("Enter your name: ")
    email = input("Enter a unique email: ")
    birth_year = int(input("Enter your birth year: "))
    faculty_name = input("Enter your faculty name: ")
    password = input("Create a password: ")

    # Check if the email is already registered
    check_email_query = 'SELECT * FROM members WHERE email=?'
    check_email_parameters = (email)
    
    existing_user = executeQuery(check_email_query, check_email_parameters)

    if existing_user:
        print("Email already registered. Please use a different email.")
    else:
        # Insert new user into the database
        register_query = '''
            INSERT INTO members (name, email, birth_year, faculty_name, passwd)
            VALUES (?, ?, ?, ?, ?)
        '''
        register_parameters = (name, email, birth_year, faculty_name, password)

        executeQuery(register_query, register_parameters)
        conn.commit()
        print("Signup successful! You can now login.")



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

conn.close()	
