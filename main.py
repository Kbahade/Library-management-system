import sqlite3
import datetime

# to connect the sql database
def create_connection():
    connection = None
    try:
        connection = sqlite3.connect('new_library.db') 
    except sqlite3.Error as e:
        print(f"Error: {e}")
    return connection

def initialize_database():
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()

            # for Creating new tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT UNIQUE,
                    password TEXT,
                    role TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    isbn TEXT,
                    genre TEXT,
                    availability INTEGER
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    book_id INTEGER,
                    timestamp DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (book_id) REFERENCES books(id)
                )
            ''')

            connection.commit()
            print("Database initialized successfully")
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

def add_user(name, email, password, role):
    connection = create_connection()
    if connection is not None:
        try:
            # Check if the email is a Gmail address
            if email.lower().endswith(("gmail.com", "gmail.org", "gmail.in")):
                # Check if the password is strong
                if (
                    len(password) >= 6
                    and any(c.isalpha() for c in password)
                    and any(c.isdigit() for c in password)
                    and any(c.isascii() and not c.isalnum() for c in password)
                ):
                    # Check if the name contains only alphabets
                    if name.isalpha():
                        cursor = connection.cursor()
                        cursor.execute(
                            '''
                            INSERT INTO users (name, email, password, role)
                            VALUES (?, ?, ?, ?)
                        ''',
                            (name, email, password, role),
                        )
                        connection.commit()
                        print("User added successfully")
                    else:
                        print("Invalid name. Please use only alphabets.")
                else:
                    print(
                        "Weak password. Please use at least 6 characters, 1 alphabet, 1 number, and 1 special character."
                    )
            else:
                print("Invalid email. Please use a Gmail address.")
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()
 

def add_book(title, author, isbn, genre, availability):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO books (title, author, isbn, genre, availability)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, author, isbn, genre, availability))
            connection.commit()
            print("Book added successfully")
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

def list_books():
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT id, title, author, genre, availability FROM books')
            books = cursor.fetchall()

            if not books:
                print("No books available.")
            else:
                print("\nList of Books:")
                for book in books:
                    book_id, title, author, genre, availability = book
                    print(f"{book_id}. {title} by {author} - Genre: {genre}, Available: {availability}")
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

            
def get_book_id_by_name_author(book_name, author):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM books WHERE title = ? AND author = ?', (book_name, author))
            book = cursor.fetchone()

            return book[0] if book else None

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

    return None

def borrow_book(user_id):
    connection = create_connection()
    if connection is not None:
        try:
            # to get book details from the user
            book_name = input("Enter the name of the book you want to borrow: ")
            author = input("Enter the author of the book: ")

            # to get the book ID based on name and author
            book_id = get_book_id_by_name_author(book_name, author)

            if book_id is not None:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO transactions (user_id, book_id, timestamp)
                    VALUES (?, ?, ?)
                ''', (user_id, book_id, datetime.datetime.now()))

                # Update book availability
                cursor.execute('''
                    UPDATE books
                    SET availability = availability - 1
                    WHERE id = ?
                ''', (book_id,))

                connection.commit()
                print("Book borrowed successfully")
            else:
                print("Book not found. Please check the name and author.")

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()


def get_borrowed_book_id_by_name_author(user_id, book_name, author):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT books.id
                FROM books
                JOIN transactions ON books.id = transactions.book_id
                WHERE transactions.user_id = ? AND books.title = ? AND books.author = ?
            ''', (user_id, book_name, author))
            book = cursor.fetchone()

            return book[0] if book else None

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

    return None

def return_book(user_id, book_name, author):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()

            borrowed_book_id = get_borrowed_book_id_by_name_author(user_id, book_name, author)

            if borrowed_book_id:
                cursor.execute('''
                    SELECT transactions.id, transactions.timestamp
                    FROM transactions
                    WHERE transactions.user_id = ? AND transactions.book_id = ?
                ''', (user_id, borrowed_book_id))

                transaction = cursor.fetchone()

                if transaction:
                    # for calculating the penalty
                    borrow_date = datetime.datetime.strptime(transaction[1], '%Y-%m-%d %H:%M:%S.%f')
                    return_date = datetime.datetime.now()
                    days_borrowed = (return_date - borrow_date).days

                    penalty = max(0, days_borrowed - 5) * 2

                    
                    cursor.execute('''
                        UPDATE books
                        SET availability = availability + 1
                        WHERE id = ?
                    ''', (borrowed_book_id,))

                    # Delete the transaction record
                    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction[0],))

                    connection.commit()

                    if penalty > 0:
                        print(f"Book returned successfully. Penalty: ${penalty}")
                    else:
                        print("Book returned successfully. No penalty.")
                else:
                    print("You haven't borrowed this book.")
            else:
                print("Book not found or not borrowed by the user. Please check.")

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()


def delete_book():
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()

            # Ask for book details
            title = input("Enter the title of the book to delete: ")
            author = input("Enter the author of the book to delete: ")

            # Check if the book exists
            cursor.execute('SELECT * FROM books WHERE title = ? AND author = ?', (title, author))
            book = cursor.fetchone()

            if book:
                # Delete the book
                cursor.execute('DELETE FROM books WHERE id = ?', (book[0],))
                connection.commit()
                print(f"Book '{title}' by {author} deleted successfully.")
            else:
                print(f"Book '{title}' by {author} not found in our list.")

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

def available_books():
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT id, title, author FROM books WHERE availability > 0')
            available_books = cursor.fetchall()

            if not available_books:
                print("No available books.")
            else:
                print("\nAvailable Books:")
                for book in available_books:
                    book_id, title, author = book
                    print(f"{book_id}. {title} by {author}")
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()  

def find_book(title):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM books WHERE title = ?', (title,))
            book = cursor.fetchone()

            if book:
                print("Book found:")
                print(f"Title: {book[1]}")
                print(f"Author: {book[2]}")
                print(f"ISBN: {book[3]}")
                print(f"Genre: {book[4]}")
                print(f"Availability: {book[5]}")
            else:
                print(f"Book '{title}' not found.")
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()
          


def update_book(title):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM books WHERE title = ?', (title,))
            book = cursor.fetchone()

            if book:
                print("Current Book Information:")
                print(f"Title: {book[1]}")
                print(f"Author: {book[2]}")
                print(f"ISBN: {book[3]}")
                print(f"Genre: {book[4]}")
                print(f"Availability: {book[5]}")

                new_title = input("Enter the new title: ")
                new_author = input("Enter the new author: ")
                new_isbn = input("Enter the new ISBN: ")
                new_genre = input("Enter the new genre: ")
                new_availability = int(input("Enter the new availability: "))

                cursor.execute('''
                    UPDATE books
                    SET title = ?, author = ?, isbn = ?, genre = ?, availability = ?
                    WHERE id = ?
                ''', (new_title, new_author, new_isbn, new_genre, new_availability, book[0]))

                connection.commit()
                print("Book updated successfully.")
            else:
                print(f"Book '{title}' not found.")
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

def login_user(email, password):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM users WHERE email = ? AND password = ?', (email, password))
            user_id = cursor.fetchone()

            return user_id[0] if user_id else None

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

    return None

def get_user_id(email):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user_id = cursor.fetchone()

            return user_id[0] if user_id else None

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

    return None

def user_transactions():
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT users.name, transactions.id, books.title, transactions.timestamp
                FROM transactions
                JOIN books ON transactions.book_id = books.id
                JOIN users ON transactions.user_id = users.id
            ''')

            all_user_transactions = cursor.fetchall()

            if not all_user_transactions:
                print("No transactions found.")
            else:
                print("\nAll User Transactions:")
                for user_transaction in all_user_transactions:
                    user_name, transaction_id, book_title, timestamp = user_transaction
                    print(f"User: {user_name}, Transaction ID: {transaction_id}, Book: {book_title}, Timestamp: {timestamp}")

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

def delete_user(email):
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()

            # Check if the user exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user_id = cursor.fetchone()

            if user_id:
                # Delete user and associated transactions
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id[0],))
                cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id[0],))

                connection.commit()
                print(f"User '{email}' deleted successfully.")
            else:
                print(f"User '{email}' not found.")

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()


# Main function
if __name__ == "__main__":

    initialize_database()

    while True:
        print("\nLibrary Management System:")
        print("1. Admin")
        print("2. Sign Up or Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1": 
            admin_password = input("Enter admin password: ")
            if admin_password == "admin":  
                while True:
                    print("\nAdmin Menu:")
                    print("1. Add Book")
                    print("2. Delete Book")
                    print("3. Update Book")
                    print("4. List Books")
                    print("5. Available Books")
                    print("6. User Transactions")
                    print("7. Delete User")
                    print("8. Exit")

                    admin_choice = input("Enter your choice: ")

                    if admin_choice == "1":  
                        title = input("Enter the title: ")
                        author = input("Enter the author: ")
                        isbn = input("Enter the ISBN: ")
                        genre = input("Enter the genre: ")
                        availability = int(input("Enter the number of copies available: "))
                        add_book(title, author, isbn, genre, availability)
                    elif admin_choice == "2":  
                        delete_book()

                    elif admin_choice == "3":  
                        title = input("Enter the title of the book to update: ")
                        update_book(title)

                    elif admin_choice == "4":  
                        list_books()

                    elif admin_choice == "5":  
                        available_books()

                    elif admin_choice == "6":  
                        user_transactions()

                    elif admin_choice == "7":  
                        email = input("Enter the email of the user to delete: ")
                        delete_user(email)

                    elif admin_choice == "8":  
                        break
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("Incorrect admin password. Access denied.")
        elif choice == "2":  
            print("1. Sign Up")
            print("2. Login")
            print("3. Exit")

            auth_choice = input("Enter your choice: ")

            if auth_choice == "1":  
                while True:
                    name = input("Enter your name: ")
                    if name.isalpha():
                        break
                    else:
                        print("Invalid name. Please use only alphabets.")

                while True:
                    email = input("Enter your email: ")
                    if email.lower().endswith(("gmail.com", "gmail.org", "gmail.in")):
                        break
                    else:
                        print("Invalid email. Please use a Gmail address.")

                while True:
                    password = input("Create a password: ")
                    if (
                        len(password) >= 6
                        and any(c.isalpha() for c in password)
                        and any(c.isdigit() for c in password)
                        and any(c.isascii() and not c.isalnum() for c in password)
                    ):
                        break
                    else:
                        print(
                            "Weak password. Please use at least 6 characters, 1 alphabet, 1 number, and 1 special character."
                        )

                add_user(name, email, password, "user")
                print("Sign up successful.")

                
                user_id = get_user_id(email)  
                while True:
                    print("\nUser Menu:")
                    print("1. Borrow a Book")
                    print("2. Return a Book")
                    print("3. List Books")
                    print("4. Find Book")
                    print("5. Exit")

                    user_action = input("Enter your choice: ")
                    if user_action == "1":  
                        borrow_book(user_id)

                    if user_action == "2":  
                        return_book(user_id)

                    elif user_action == "3":  
                        list_books()

                    elif user_action == "4":  
                        title = input("Enter the title of the book you want to find: ")
                        find_book(title)

                    elif user_action == "5":  
                        print("Exiting User Menu. Goodbye!")
                        break

                    else:
                        print("Invalid choice. Please try again.")

            elif auth_choice == "2":  
                email = input("Enter your email: ")
                password = input("Enter your password: ")

                user_id = login_user(email, password)  
                if user_id:
                    print("Login successful.")

                    user_id = get_user_id(email)  
                    print("\nUser Menu:")
                    print("1. Borrow a Book")
                    print("2. Return a Book")
                    print("3. List Books")
                    print("4. Find Book")
                    print("5. Exit")

                    user_action = input("Enter your choice: ")

                    if user_action == "1": 
                        book_id = input("Enter the ID of the book you want to borrow: ")
                        borrow_book(user_id, book_id)

                    elif user_action == "2":  
                        print("Return a Book:")
                        book_name = input("Enter the name of the book you want to return: ")
                        author = input("Enter the author of the book: ")
                        return_book(user_id, book_name, author)

                    elif user_action == "3":  
                        list_books()

                    elif user_action == "4":  
                        title = input("Enter the title of the book you want to find: ")
                        find_book(title)

                    elif user_action == "5":  
                        print("Exiting User Menu. Goodbye!")
                        break

                    else:
                        print("Invalid choice. Please try again.")
   
                else:
                    print("Invalid email or password. Please try again.")

            elif auth_choice == "3":  
                print("Exiting Library Management System. Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")

        elif choice == "3":
            print("Exiting Library Management System. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")
        