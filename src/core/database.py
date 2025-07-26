import sqlite3
from core.__init__ import DATABASE_FILE
import sys

class Database:
  def __init__(self):
    self.name_file_databse = DATABASE_FILE

    self.conn = sqlite3.connect(self.name_file_databse)
    self.cursor = self.conn.cursor()

    self.create_tables()

  def create_tables(self):
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL
                        )
                        """)

    self.cursor.execute("""CREATE TABLE IF NOT EXISTS sessions 
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        time INTEGER,
                        description TEXT,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
                        )""")
    
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS projects 
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        status TEXT,
                        time INTEGER,
                        description TEXT,
                        folder TEXT,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
                        )""")
    
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS projects_tasks
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        status TEXT,
                        description TEXT,
                        project_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(project_id) REFERENCES projects(id) on DELETE CASCADE
                        FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
                        )""")

    self.conn.commit()