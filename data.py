import sqlite3
def create_connection():
    connection = None
    try:
        connection = sqlite3.connect('new_library.db')  # 'library.db' is the SQLite database file
        print(f"Connection to SQLite DB  successful")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    return connection
def fetch_and_print_users():
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()

            if not users:
                print("No users in the database.")
            else:
                print("\nUsers:")
                for user in users:
                    print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Role: {user[4]}")

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

def fetch_and_print_books():
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM books')
            books = cursor.fetchall()

            if not books:
                print("No books in the database.")
            else:
                print("\nBooks:")
                for book in books:
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Genre: {book[4]}, Availability: {book[5]}")

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

def fetch_and_print_transactions():
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM transactions')
            transactions = cursor.fetchall()

            if not transactions:
                print("No transactions in the database.")
            else:
                print("\nTransactions:")
                for transaction in transactions:
                    print(f"ID: {transaction[0]}, User ID: {transaction[1]}, Book ID: {transaction[2]}, Timestamp: {transaction[3]}")

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            connection.close()

# Call the functions to print the contents of each table
fetch_and_print_users()
fetch_and_print_books()
fetch_and_print_transactions()
