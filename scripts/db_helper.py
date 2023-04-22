import sqlite3
from user import User
from service import Service


class DBHelper:
    def __init__(self):
        self.conn = sqlite3.connect("./db/users.db",check_same_thread=False)
        cursor = self.conn.cursor()
        try:
            cursor.execute("create table users(username UNIQUE,password)")
        except sqlite3.OperationalError:
            print("Table users already exists, continuing with previous data.")
        try:
            cursor.execute("create table services(name UNIQUE,secret_key)")
        except sqlite3.OperationalError:
            print("Table services already exists, continuing with previous data.")
            
    # Requests handling fetching
    def fetch_user(self, username):
        cursor = self.conn.cursor()
        query = cursor.execute("select * from users where users.username = "+"'"+username+"'")
        username, password = query.fetchone()
        user = User(username, password)
        if user is None:
            return -1, "User dosen't exist."
        else :
            return 1, user
    def fetch_service(self, service_name):
        cursor = self.conn.cursor()
        query = cursor.execute("select * from services where services.name = "+"'"+service_name+"'")
        service_name, secret_key = query.fetchone()
        service = Service(service_name, secret_key)
        return service

    # Requests handling insertions
    def add_user(self, username, password):
        cursor = self.conn.cursor()
        insert_query = cursor.execute("insert into users values ('"+username+"','"+password+"')")
        self.conn.commit()
    def add_service(self, service, secret_key):
        cursor = self.conn.cursor()
        insert_query = cursor.execute("insert into services values ('"+service+"','"+secret_key+"')")
        self.conn.commit()

    # For testing purposes.
    def dummy_insert(self):
        cursor = self.conn.cursor()
        insert_query = cursor.execute("insert into users values ('hedi','hedi'), ('kawkaw','kawkaw')")
        self.conn.commit()
    def fetch_all(self):
        cursor = self.conn.cursor()
        query = cursor.execute("select * from users")
        users = query.fetchall()
        return users
    def delete_dummy_insert(self):
        cursor = self.conn.cursor()
        query = cursor.execute("delete from users where username ='hedi' or username='kawkaw'")
        self.conn.commit()
    def close(self):
        self.conn.close()