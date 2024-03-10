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







def searchBooks(userEmail):
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
    SELECT b.book_id, title, author, pyear, IFNULL(rating, 0), 
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


    WITH RankedBooks AS (
        SELECT
            book_id,
            title,
            author,
            pyear,
            ROW_NUMBER() OVER (
                ORDER BY
                    CASE
                        WHEN title LIKE '%' || 'hokage' || '%' THEN 1
                        ELSE 2
                    END,
                    CASE
                        WHEN title LIKE '%' || 'hokage' || '%' THEN title
                        ELSE author
                    END
            ) AS RowNum
        FROM books
        WHERE title LIKE '%' || 'hokage' || '%' OR author LIKE '%' || 'hokage' || '%'
    )
    /* Select the books from RankedBooks and then join more info onto the rows */
    SELECT b.book_id, title, author, pyear, IFNULL(rating, 0), (SELECT COUNT(*) FROM RankedBooks),
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
    WHERE RowNum > 5 * (1 - 1) AND RowNum <= 5 * 1;
    '''
    # Now for the real function
    keyword = input('Enter a search keyword to find books of: ')
    pageNum = 1

    queryParams = {'keyword': keyword, 'page': pageNum}

    results = executeQuery(queryOfPain, queryParams)
    #print(results) #temp
    for row in results:
        print(row) # still somewhat temp

    # Next, ask to see another page (should we have a way to know the number of total results?)

    # Also there needs to be a prompt to be able to borrow any book there (if possible)



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
        searchBooks()



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
    response = input("What would you like to do? ")
    if response.lower() in ['view info', 'view borrowings', 'search books', 'pay penalty', 'search books']:
        print('alright we\'ll do that for you then (program the doing it for them)')
        doAction(response)
    elif response != 'quit':
        print("Invalid option")

print('the end')

#conn.commit() # if you want to save changes to the db
conn.close()	
