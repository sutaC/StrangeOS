import sqlite3

class Kernel:
    def __init__(self) -> None:
        print("Kernel connecting...")
        self.__conn: sqlite3.Connection = sqlite3.connect("filesystem.db") 
        # Inits database
        cursor = self.__conn.cursor()
        # Creates tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL,
                parent_id INTEGER, 
                type TEXT CHECK(type IN ('file', 'directory')) NOT NULL, 
                FOREIGN KEY (parent_id) REFERENCES nodes(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                node_id INTEGER PRIMARY KEY, 
                metadata TEXT,
                data BLOB, 
                FOREIGN KEY (node_id) REFERENCES nodes(id)
            )
        ''')
        self.__conn.commit() # Adds tables if empty
        ROOT = cursor.execute('''
            SELECT id FROM nodes WHERE parent_id IS NULL
        ''').fetchone()
        if ROOT is None: # Adds root directory if doesn't exist
            cursor.execute('''
                INSERT INTO nodes (id, name, parent_id, type) VALUES (NULL, 'root', NULL, 'directory')               
            ''')
            self.__conn.commit()  
        cursor.close()
        print("Kernel connected")

    def __del__(self) -> None:
        print("Closing kernel connection...")
        self.__conn.close()
        print("Kernel connection closed")