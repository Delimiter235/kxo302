# db_manager.py

import sqlite3


def connect_db():  # function to connect to the database
    return sqlite3.connect('database.db')



def query_all_users():  # function to query all users
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()

    return rows


def query_user_by_name(username):  # function to query a user by user's name
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()

    return rows


def insert_user(user_data):  # function to insert a new user
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, gender, age, favorite_genre, is_admin) VALUES (?, ?, ?, ?, ?, ?)", (user_data))
    conn.commit()
    conn.close()


def update_user(user_data):  # function to update a user's information
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET age = ? WHERE username = ?", (user_data))
    conn.commit()
    conn.close()


def delete_user(username):  # function to delete a user
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()