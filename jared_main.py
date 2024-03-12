import sqlite3
import sys
import getpass
import math

if len(sys.argv) != 2:
    print("Usage: python3 main.py <database_name>")
    sys.exit(1)

#  ------------------------ GLOBAL VARIABLES ---------------------------------

DB_PATH = sys.argv[1]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

LOGGED_IN_USER = None
# ----------------------------------------------------------------------------


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
    if name == '':
        print('Name cannot be left blank, registration cancelled\n')
        return
    email = input("Enter a unique email: ")
    if email == '':
        print('Email cannot be left blank, registration cancelled\n')
        return
    try:
        birth_year = int(input("Enter your birth year: "))
    except:
        print("Invalid age, registration stopped.\n")
        return
    faculty_name = input("Enter your faculty name: ")
    password = getpass.getpass("Create a password: ")
    if password == '':
        print('Password cannot be left blank, registration cancelled\n')
        return

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

#-----------------------PART 1 starts HERE-------------------------------------------------
#-----------------------PART 1 ends HERE-------------------------------------------------

#-----------------------PART 2 starts HERE-------------------------------------------------
#-----------------------PART 2 ends HERE-------------------------------------------------

#-----------------------PART 3 starts HERE-------------------------------------------------
def printAndSortResults(results, totalResults, pageNum):
    #print(f'\n{totalResults} results found, showing {5 * pageNum - 4} to {min(totalResults, 5 * pageNum)}')
    print(f'\n{totalResults} results found, showing page {pageNum} of {math.ceil(totalResults / 5)}')
    print('%7s | %30s | %30s | %4s | %10s | %10s' % ('Book ID', 'Title'.center(30), 'Author'.center(30), 'Year', 'Avg Rating', 'Available?'))
    borrowables = []
    booksOnScreen = []
    for row in results:
        print('%7d | %30s | %30s | %4d | %10s | %10s' % (row[0], row[1], row[2], row[3], row[4], row[6]))
        booksOnScreen.append(row[0])
        if row[6] == 'Available':
            borrowables.append(row[0])
    return (booksOnScreen, borrowables)



def borrowBook(bookID, booksOnScreen, borrowables):
    if bookID in borrowables:
        print('ayo borrow this book!!!!', bookID) # SOMEONE WRITE THIS
        # will need to do an insert into borrowings statement here
        return True
    elif bookID in booksOnScreen:
        print('This book is currently being borrowed!')
        return False
    else:
        print('This book isn\'t being shown in the list currently!')
        return False

printOtherText = True
def getOtherResponse(curPage, totalResults):
    '''
    Return value 0 signals flip page, return value 1 signals search, 2 signals borrow, 3 signals return
    '''
    maxPages = math.ceil(totalResults / 5)
    global printOtherText
    if printOtherText:
        print("\nOptions: \n-page x (flips to page x)\n-next (flips to next page)\n-prev (flips to previous page)\n-borrow x (borrows book with ID x)\n-search (prompts for a new search)\n")
    printOtherText = True

    while True:
        response = input('Choose a menu option or \'return\' to exit: ').lower()

        if 'page' in response:
            try:
                pageNumber = int(response.split()[-1])
                if pageNumber >= 1 and pageNumber <= maxPages:
                    return [0, pageNumber]
                else:
                    print('Invalid page number (not within the existing range)')
            except:
                print('Invalid page number (not an integer)')
        elif response == 'next':
            if curPage + 1 <= maxPages:
                return [0, curPage + 1]
            else:
                print('No more pages after this one')
        elif response == 'prev':
            if curPage - 1 >= 1:
                return [0, curPage - 1]
            else:
                print('No more pages before this one')
        elif 'borrow' in response:
            try:
                bookID = int(response.split()[-1])
                printOtherText = False
                return [2, bookID]
            except:
                print('Unable to read book ID (not an integer)')
        elif response == 'search':
            return [1]
        elif response == 'return':
            return [3,]
        else:
            print('Unable to read command, try again')
            


def getRetryResponse():
    while True:
        response = input('No books found, want to return to main menu? (y/n): ').lower()
        if response == 'y':
            return False
        elif response == 'n':
            return True
        else:
            print("Invalid option, input 'y' or 'n'")

def searchBooks(userEmail):
    global printOtherText
    # Jared - I received some advice from a TA (Farishta) with writing my SQL
    # query for the Search Books function, particularly with how to write the
    # ORDER BY clause to sort the results properly.
    queryOfPain = '''
    WITH RankedBooks AS (
        SELECT
            book_id,
            title,
            author,
            pyear,
            ROW_NUMBER() OVER (
                ORDER BY
                    CASE
                        WHEN title LIKE '%' || :keyword || '%' THEN 1
                        ELSE 2
                    END,
                    CASE
                        WHEN title LIKE '%' || :keyword || '%' THEN title
                        ELSE author
                    END
            ) AS RowNum
        FROM books
        WHERE title LIKE '%' || :keyword || '%' OR author LIKE '%' || :keyword || '%'
    )
    /* Select the books from RankedBooks and then join more info onto the rows */
    SELECT b.book_id, title, author, pyear, IFNULL(rating, 'N/A'), (SELECT COUNT(*) FROM RankedBooks),
    (CASE WHEN borrowed='BORROWED' THEN 'Borrowed' ELSE 'Available' END) AS borrowed
    FROM RankedBooks b
    LEFT JOIN (
        /* Finds the avg rating per book */
        SELECT book_id, IFNULL(AVG(rating), 0) AS rating
        FROM reviews
        GROUP BY book_id) ratings
    ON ratings.book_id=b.book_id
    LEFT JOIN (
        /* Gets all books that are currently borrowed */
        SELECT books.book_id, 'BORROWED' as borrowed
            FROM books
            INNER JOIN borrowings brrw
            ON brrw.book_id=books.book_id
            WHERE end_date IS NULL) in_use
    ON in_use.book_id=b.book_id
    WHERE RowNum > 5 * (:page - 1) AND RowNum <= 5 * :page;
    '''
    # Now for the real function
    # Provide as many search prompts as desired until a return prompt is received
    while True:
        # Initialize the search keyword and run the query
        keyword = input('Enter a search keyword to find books of: ')
        pageNum = 1

        queryParams = {'keyword': keyword, 'page': pageNum}
        results = executeQuery(queryOfPain, queryParams)
        
        # If some books were found, provide all the options for viewing them
        if len(results) != 0:
            totalResults = results[0][5]
            booksOnScreen, borrowables = printAndSortResults(results, totalResults, pageNum)

            # Keep asking to flip page or borrow a book until asked to return
            while True:
                choice = getOtherResponse(pageNum, totalResults)
                if choice[0] == 0: # flip page (requires re-running query)
                    pageNum = choice[1]
                    queryParams = {'keyword': keyword, 'page': pageNum}
                    results = executeQuery(queryOfPain, queryParams)
                    booksOnScreen, borrowables = printAndSortResults(results, totalResults, pageNum)
                elif choice[0] == 1: # Choose new search term
                    break
                elif choice[0] == 2: # Borrow a book
                    successfulBorrow = borrowBook(choice[1], booksOnScreen, borrowables)
                    if successfulBorrow:
                        printOtherText = True
                        booksOnScreen, borrowables = printAndSortResults(results, totalResults, pageNum)
                elif choice[0] == 3: # Return to main menu
                    return
        # If no books were found, ask to try again or return to main menu
        else:
            if getRetryResponse() == False:
                return
            

#-----------------------PART 3 ends HERE-------------------------------------------------

#-----------------------PART 4 starts HERE-------------------------------------------------
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
#--------------------------- PART 4 ENDS HERE --------------------------------        
        
def doAction(action):
    if action == 'view info':
        pass
    elif action == 'view borrowings':
        pass
    elif action == 'search books':
        searchBooks(LOGGED_IN_USER)
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
    print("Menu: \n-view info\n-view borrowings\n-search books\n-pay penalty\n")
    
    response = input("What would you like to do (type in the menu options or 'quit' to exit): ")
    
    if response.lower() in ['view info', 'view borrowings', 'search books', 'pay penalty']:
        doAction(response)
    elif response != 'quit':
        print("Invalid option")

print('the end')

#conn.commit() # if you want to save changes to the db
conn.close()	
