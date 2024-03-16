import sqlite3
import sys
import getpass
import math
import datetime
from datetime import date

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

def executeQuery(query, parameters) -> list:
    if parameters is not None:
        c.execute(query, parameters)
    else:
        c.execute(query)
    rows = c.fetchall()
    return rows

def loginUser():
    global LOGGED_IN_USER
    emailVar = input("Enter your email: ")
    passwordVar = getpass.getpass("Enter your password: ")

    login_query = 'SELECT * FROM members WHERE LOWER(email)=? AND passwd=?'
    login_parameters = (emailVar.lower(), passwordVar)
    
    user = executeQuery(login_query, login_parameters)

    if user:
        print(f"Hello, {user[0][2]}!\n")
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
        current_year = datetime.datetime.now().year
        if birth_year > current_year:
            print("Birth year cannot be in the future.")
            return
    except ValueError:
        print("Invalid year format, registration stopped.\n")
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
def viewMemberProfile():
    if LOGGED_IN_USER is None:
        print("You must be logged in to view your profile.")

    # Fetch personal information
    personal_info_query = 'SELECT name, email, byear FROM members WHERE email=?'
    personal_info = executeQuery(personal_info_query, (LOGGED_IN_USER,))

    # Fetch borrowing information
    borrowing_query = '''
    SELECT
        (SELECT COUNT(*) FROM borrowings WHERE member=? AND end_date IS NOT NULL) AS previous_borrowings,
        (SELECT COUNT(*) FROM borrowings WHERE member=? AND end_date IS NULL) AS current_borrowings,
        (SELECT COUNT(*) FROM borrowings WHERE member=? AND end_date IS NULL AND julianday('now') - julianday(start_date) > 20) AS overdue_borrowings
    '''
    borrowing_info = executeQuery(borrowing_query, (LOGGED_IN_USER, LOGGED_IN_USER, LOGGED_IN_USER))

    # Fetch penalty information
    penalty_query = '''
    SELECT
        (SELECT COUNT(*) FROM penalties p JOIN borrowings b ON p.bid=b.bid WHERE b.member=? AND paid_amount < amount) AS unpaid_penalties,
        (SELECT SUM(amount - paid_amount) FROM penalties p JOIN borrowings b ON p.bid=b.bid WHERE b.member=? AND paid_amount < amount) AS total_debt
    '''
    penalty_info = executeQuery(penalty_query, (LOGGED_IN_USER, LOGGED_IN_USER))

    # Print the information
    print("\nMember Profile:")
    print(f"Name: {personal_info[0][0]}\nEmail: {personal_info[0][1]}\nBirth Year: {personal_info[0][2]}")
    print(f"Previous Borrowings: {borrowing_info[0][0]}, Current Borrowings: {borrowing_info[0][1]}, Overdue Borrowings: {borrowing_info[0][2]}")
    print(f"Unpaid Penalties: {penalty_info[0][0]}, Total Debt on Penalties: {penalty_info[0][1] if penalty_info[0][1] else 0}\n")
#-----------------------PART 1 ends HERE-------------------------------------------------

#-----------------------PART 2 starts HERE-------------------------------------------------
def returnBook():

    if LOGGED_IN_USER is None:
        print("You must be logged in to return a book.")
        return

    try:

        # fetch user's CURRENT borrowings query
        current_borrowings_query = ''' 
        SELECT bid, books.book_id, title, start_date
        FROM borrowings
        JOIN books ON books.book_id = borrowings.book_id
        WHERE member=? 
        AND 
        end_date IS NULL
        '''

        # borrowings returns a list
        borrowings = executeQuery(current_borrowings_query, (LOGGED_IN_USER,))
        conn.commit()

        # case where user has no borrowings
        if not borrowings:
            print("You have no current borrowings to return.")
            return
        
        # print borrowings and calculate the deadline of each one 
        print("Your current borrowings:")
        for borrowing in borrowings:

            #get deadline query 
            deadline_query = '''
            SELECT date(start_date, '+20 days') as deadline 
            FROM borrowings 
            WHERE bid=?
            '''
            deadline_result = executeQuery(deadline_query, (borrowing[0],))
            conn.commit()

            #extract from list 
            if deadline_result:
                deadline = deadline_result[0][0]
            else:
                deadline_result = "N/A"
            
            #display bid, book id, title, start date and deadline:
            print(f"Borrowing ID: {borrowing[0]}, Book ID: {borrowing[1]}, Title: {borrowing[2]}, Start Date: {borrowing[3]}, Deadline: {deadline}")

        # next prompt user if they want to return a book
        bid_to_return = input("Enter the borrowing ID of the book to return: ")

        #find instance of borrowing in table
        selected_borrowing = next((b for b in borrowings if str(b[0]) == bid_to_return), None)

        if not selected_borrowing:
            print("Invalid borrowing ID.")
            return

        # Calculate the number of overdue days, adjusted for a timezone offset of -6 hours (MDT)
        overdue_days_query = '''
        SELECT 
            CASE 
                WHEN julianday('now') - 0.25 - julianday(start_date) > 20 THEN 
                    julianday('now') - 0.25 - julianday(start_date) - 20 
                ELSE 0 
            END as overdue_days
        FROM borrowings
        WHERE bid=?
        '''

        # returns something like [(19.993999583180994,)] so we need next block
        overdue_days_result = executeQuery(overdue_days_query, (bid_to_return,))
        conn.commit()
        print(overdue_days_result)

        #get element from list 
        if overdue_days_result and overdue_days_result[0][0] > 0:
            overdue_days = overdue_days_result[0][0] 
        else:
            overdue_days = 0
        
        #round down 
        overdue_days = math.floor(overdue_days)

        # TESTING OMIT
        penalty_amount = overdue_days
        print(f"Applying a penalty of ${penalty_amount} for the overdue return of '{selected_borrowing[2]}'.") 

        # if overdue, apply penalty 
        if overdue_days > 0:
            penalty_amount = overdue_days  # $1 per overdue day
            print(f"Applying a penalty of ${penalty_amount} for the overdue return of '{selected_borrowing[2]}'.")

            insert_penalty_query = '''
            INSERT INTO penalties (bid, amount, paid_amount) 
            VALUES (?, ?, 0)
            '''
            executeQuery(insert_penalty_query, (bid_to_return, penalty_amount))
            conn.commit()

        # mark the book as returned 
        return_book_query = '''
        UPDATE borrowings 
        SET end_date=date('now') 
        WHERE bid=?
        '''

        executeQuery(return_book_query, (bid_to_return,))
        conn.commit()
        print(f"Book '{selected_borrowing[2]}' returned successfully.")

        # ask for a review with the option to decline
        while True:
            review_decision = input("Would you like to leave a review for this book? (yes/no): ").lower()
            if review_decision == 'yes':
                rating = input("Rating (1-5): ")
                if not rating.isdigit() or not 1 <= int(rating) <= 5:
                    print("Invalid rating. Please enter a number between 1 and 5.")
                    continue
                review_text = input("Review: ")

                #this query treats RID as an alias for ROWID, add review
                insert_review_query = '''
                    INSERT INTO reviews (book_id, member, rating, rtext, rdate)  
                    VALUES (?, ?, ?, ?, datetime('now'))
                '''
                executeQuery(insert_review_query, (selected_borrowing[1], LOGGED_IN_USER, rating, review_text))
                conn.commit()
                print("Thank you for your review!")
                break
            elif review_decision == 'no':
                break
            else:
                print("Invalid option. Please answer 'yes', 'no'.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

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
        maxBID = executeQuery('SELECT MAX(bid) FROM borrowings;', None)[0][0]
        
        borrowQuery = 'INSERT INTO borrowings VALUES (?, ?, ?, ?, ?)'
        borrowParams = (maxBID + 1, LOGGED_IN_USER, bookID, date.today(), None)
        executeQuery(borrowQuery, borrowParams)
        conn.commit()
        print(f'Book {bookID} has been borrowed!')
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
                        results = executeQuery(queryOfPain, queryParams) # Refresh to show the new book has been borrowed
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
            print(f"Penalty ID: {penalty[0]}, Amount: ${penalty[2] - penalty[3]:.2f}\n")
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
                return
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
    
    while True:
        quit = input("Back to menu? (y/n): ")
        if quit.lower() == 'n':
            print()
            pay_penalty(user_email)
            break  # Exit the loop after executing the function
        elif quit.lower() == 'y':
            print()
            return  # Exit the function, thus ending the loop
        else:
            print("Please enter 'y' for yes or 'n' for no.")
#--------------------------- PART 4 ENDS HERE --------------------------------        
        
def doAction(action):
    if action == 'view info':
        viewMemberProfile()
    elif action == 'return book':
        returnBook()
    elif action == 'search books':
        searchBooks(LOGGED_IN_USER)
    elif action == 'pay penalty':
        pay_penalty(LOGGED_IN_USER)

# -------------------------------- MAIN --------------------------------------

# Do not let the user through until they have logged in
response = ''
validResponse = False
# Replace the existing loop at the bottom of your script with this:
while True:
    if LOGGED_IN_USER is None:
        response = ''
        while response not in ['login', 'register']:
            response = input("Would you like to login, register, or quit? ").lower()
            if response == 'login':
                loginUser()
            elif response == 'register':
                registerUser()
            elif response == 'quit':
                print("Exiting...")
                conn.close()
                sys.exit(0)
            else:
                print("Invalid response, type either 'login', 'register', or 'quit'")
    
    print("Menu: \n-view info\n-return book\n-search books\n-pay penalty\n-logout\n")
    
    response = input("What would you like to do (type in the menu options or 'quit' to exit): ").lower()
    
    if response in ['view info', 'return book', 'search books', 'pay penalty']:
        doAction(response)
    elif response == 'logout':
        print("Logging out...\n")
        LOGGED_IN_USER = None
        continue  # This will skip the rest of the loop and go back to the login/register prompt
    elif response == 'quit':
        print('Exiting...')
        break
    else:
        print("Invalid option")

conn.close()
	