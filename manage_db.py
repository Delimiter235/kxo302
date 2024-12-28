"""
manage_db.py

This Object-Relational Mapping (ORM) script provides a simple command-line interface for interacting with an SQLite database.
It allows the manager to perform the following operations on the 'users' table:

1. Query all users: Display all records in the 'users' table
2. Query user by name: Display the specific record by username in the 'users' table
3. Insert new user: Create a record by entering information manually and insert it into the 'users' table
4. Update user: Change the specific record by entering information and save it in the 'users' table
5. Delete user: Delete the specific record by username
6. Exit: Exit the interface
"""

import db_manager
from werkzeug.security import generate_password_hash
#from passlib.context import CryptContext


#pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt"])

def show_menu():
    print("Select an option:")
    print("1. Query all users")
    print("2. Query user by name")
    print("3. Insert new user")
    print("4. Update user")
    print("5. Delete user")
    print("6. Exit")

def query_all_users():
    users = db_manager.query_all_users()

    for user in users:
        print(user)

def query_user_by_name():
    username = input("Enter the name of the user you want to query: ")

    users = db_manager.query_user_by_name(username)
    if users:
        for user in users:
            print(user)
    else:
        print("No user found with that name.")

def insert_user():
    username = input("Enter the user's name: ")

    password = input("Enter the user's password: ")
    password = generate_password_hash(password)

    gender = input("Choose the user's gender (male/female/other): ")
    if gender not in ['male', 'female', 'other']:
        print("Please choose the correct gender.")
        return

    age = input("Enter the user's age: ")
    if not age.isdigit():
        print("Please enter a valid integer as the age.")
        return

    favorite_genre = "Fiction"
    print("Default favorite book genre is set as \"Fiction\".")

    is_admin = input("Decide the user to be the administrator (y/n): ")
    if is_admin not in ['y', 'n']:
        print("Please print \"y\" or \"n\" to decide whether the user is a administrator.")
        return
    else:
        is_admin = 1 if is_admin == 'y' else 0

    user_data = [
        username,
        password,
        gender,
        age,
        favorite_genre,
        is_admin
    ]

    db_manager.insert_user(user_data)

    print(f"User {username} added successfully.")

def update_user():
    username = input("Enter the name of the user you want to update: ")
    age = input("Enter the new age: ")
    db_manager.update_user(username, int(age))
    print(f"User {username} updated successfully.")

def delete_user():
    username = input("Enter the name of the user you want to delete: ")
    db_manager.delete_user(username)
    print(f"User {username} deleted successfully.")

def main():
    while True:
        show_menu()
        choice = input("Enter your choice: ")
        
        if choice == '1':
            query_all_users()

        elif choice == '2':
            query_user_by_name()

        elif choice == '3':
            insert_user()

        elif choice == '4':
            update_user()

        elif choice == '5':
            delete_user()

        elif choice == '6':
            print("Exiting...")
            break

        else:
            print("\nInvalid choice. Please try again.\n")

if __name__ == "__main__":
    main()