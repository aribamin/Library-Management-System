import sqlite3
import sys
import getpass

# GLOBAL VARIABLES
if len(sys.argv) != 2:
    print("Usage: python3 main.py <database_name>")
    sys.exit(1)

DB_PATH = sys.argv[1]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

LOGGED_IN_USER = None

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
    global LOGGED_IN_USER
    emailVar = input("Enter your email: ")
    passwordVar = getpass.getpass("Enter your password: ")

    login_query = 'SELECT * FROM members WHERE email=? AND passwd=?'
    login_parameters = (emailVar, passwordVar)
    
    user = executeQuery(login_query, login_parameters)

    if user:
        print(f"Mogging awaits, {user[0][1]}!")
        LOGGED_IN_USER = user[0][0]
    else:
        print("Invalid email or password. Please try again.")

def registerUser():
    name = input("Enter your name: ")
    email = input("Enter a unique email: ")
    try:
        birth_year = int(input("Enter your birth year: "))
    except:
        print("Invalid age, registration stopped.\n")
        return
    faculty_name = input("Enter your faculty name: ")
    password = getpass.getpass("Create a password: ")

    # Check if the email is already registered
    check_email_query = 'SELECT * FROM members WHERE email=?'
    check_email_parameters = (email,) # must be tuple
    
    existing_user = executeQuery(check_email_query, check_email_parameters)

    if existing_user:
        print("Email already registered. Please use a different email.")
    else:
        # Insert new user into the database
        register_query = '''
            INSERT INTO members (name, email, byear, faculty, passwd)
            VALUES (?, ?, ?, ?, ?)
        '''
        register_parameters = (name, email, birth_year, faculty_name, password)

        executeQuery(register_query, register_parameters)
        conn.commit()
        print("Signup successful! You can now login.")

def any_unpaid(user_email):
    """
    Display a list of unpaid penalties for the given user or return false if there is no unpaid penalties.
    input: user_email
    """
    unpaid_query = 'SELECT * FROM penalties WHERE bid IN ' \
                    '(SELECT bid FROM borrowings WHERE member = ?) ' \
                    'AND paid_amount < amount'
    unpaid_param = (user_email,)

    unpaid_penalties = executeQuery(unpaid_query, unpaid_param)

    if unpaid_penalties:
        print("Unpaid Penalties:")
        for penalty in unpaid_penalties:
            print(f"Penalty ID: {penalty[0]}, Amount: ${penalty[2] - penalty[3]}")
    else:
        print("No unpaid penalties.\n")
        return False    
    return True

def pay_penalty(user_email):
    """
    Allow the user to select a penalty and pay it partially or in full.
    """
    if any_unpaid(user_email):

        penalty_id = input("Enter the ID of the penalty you want to pay: ")

        # Validate penalty_id
        if not penalty_id.isdigit():
            print("Invalid ID. ID must be a digit")
            quit = input("Back to menu? (y/n): ")
            if quit.lower() == 'n':
                print()
                pay_penalty(user_email)
            elif quit.lower() == 'y':
                print()
                return

        penalty_id = int(penalty_id)

        get_penalty_query = 'SELECT * FROM penalties WHERE pid = ? AND bid IN ' \
                            '(SELECT bid FROM borrowings WHERE member = ?) ' \
                            'AND paid_amount < amount'
        get_penalty_parameters = (penalty_id, user_email)

        penalty = executeQuery(get_penalty_query, get_penalty_parameters)

        if penalty:
            remaining_amount = penalty[0][2] - penalty[0][3]

            amount_to_pay = input(f"Remaining amount for Penalty ID {penalty_id}: ${remaining_amount:.2f}. "
                                "Enter the amount to pay: ")

            # Validate amount_to_pay
            try:
                amount_to_pay = float(amount_to_pay)
                if 0 < amount_to_pay <= remaining_amount:
                    update_penalty_query = 'UPDATE penalties SET paid_amount = paid_amount + ? WHERE pid = ?'
                    update_penalty_parameters = (amount_to_pay, penalty_id)

                    executeQuery(update_penalty_query, update_penalty_parameters)
                    conn.commit()

                    print(f"Payment successful! Remaining amount for Penalty ID {penalty_id}: ${(remaining_amount - amount_to_pay):.2f}")
                else:
                    print("Invalid amount. Please enter a valid amount within the remaining penalty.")
            except ValueError:
                print("Invalid amount. Please enter a valid numeric amount.")
        else:
            print("The Penalty ID entered might not exist or has been paid for already")
    else:
        return
    
    quit = input("Back to menu? (y/n): ")
    if quit.lower() == 'n':
        print()
        pay_penalty(user_email)
    elif quit.lower() == 'y':
        print()
        return
        
def doAction(action):
    #match actionVar:
    #    case 'view info':
    #        pass #do things
    #    case 'view borrowings':
    #        pass #you get the idea

    # so apparently our python is too outdated to use match case on lab machines
    if action == 'view info':
        pass
    elif action == 'view borrowings':
        pass
    elif action == 'search books':
        pass
    elif action == 'pay penalty':
        pay_penalty(LOGGED_IN_USER)


# -------------------------------- MAIN --------------------------------------

# Do not let the user through until they have logged in
response = ''
validResponse = False
while LOGGED_IN_USER is None:
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
    validResponse = False


# Now that they're logged in, give them access to the full options
response = ''
validResponse = False
while response != 'quit':
    print("Menu: \n1) view info\n2) view borrowings\n3) search books\n4) pay penalty\n")
    
    response = input("What would you like to do (type in the menu options or 'quit' to exit): ")
    
    if response.lower() in ['view info', 'view borrowings', 'search books', 'pay penalty']:
        print('alright we\'ll do that for you then (program the doing it for them)')
        doAction(response)
    elif response != 'quit':
        print("Invalid option")

print('the end')

#conn.commit() # if you want to save changes to the db
conn.close()	
