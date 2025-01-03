import sqlite3
import os
import bcrypt
from traceback import print_exc
from .io import IO
from .options import SysOptions

class MissingNodeException(Exception):
    pass
class NodeTypeException(Exception):
    pass
class NodeNameConflictException(Exception):
    pass
class SystemNodeException(Exception):
    pass
class NodeHasChildrenException(Exception):
    pass
class UserLoginException(Exception):
    pass

class Kernel:
    def __init__(self, options: SysOptions) -> None:
        self.__OPTIONS: SysOptions = options
        self.__conn:  sqlite3.Connection
        self.__root: int
        IO.write("Kernel connecting...", style=IO.Styles.dim)
        try:
            self.__initDatabase()
            self.__initFilesystem()
            self.__initUsers()
        except Exception as exc:
            IO.write(f"\nKernel error - cannot initiate system\n{exc}\System might be corrupted and not functionate correctly, try to clear filesystem and try again\n", style=IO.Styles.error)
            if self.__OPTIONS['verbose']:
                print_exc() 
                IO.write() # Whitespace
            raise SystemExit
        IO.write("Kernel connected", style=IO.Styles.dim)

    def __del__(self) -> None:
        IO.write("Closing kernel connection...", style=IO.Styles.dim)
        if hasattr(self, '__conn'):
            self.__conn.close()
        IO.write("Kernel connection closed", style=IO.Styles.dim)

    # Private
    def __initDatabase(self) -> None:
        # Creating connection
        self.__conn = sqlite3.connect(self.__OPTIONS["dbdir"]) 
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
                contents BLOB, 
                FOREIGN KEY (node_id) REFERENCES nodes(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                login TEXT PRIMARY KEY, 
                password TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        ''')
        self.__conn.commit() # Adds tables if empty
        cursor.close()

    def __initFilesystem(self) -> None:
        cursor = self.__conn.cursor()
        # Gets root dir
        self.__root = cursor.execute('''
            SELECT id FROM nodes WHERE parent_id IS NULL
        ''').fetchone()
        if self.__root is not None:
            self.__root = self.__root[0] # Dicscards tuple
            cursor.close()
            return
        else:
            # Adds root directory if doesn't exist
            cursor.execute("INSERT INTO nodes (id, name, parent_id, type) VALUES (NULL, 'root', NULL, 'directory')")
            self.__conn.commit() 
            self.__root: int = cursor.lastrowid
        cursor.close()
        # Creates file structure
        # Clears system
        self.prune_system()
        # Add folders
        HOME: int = self.create_directory("home", self.__root)
        BIN: int = self.create_directory("bin", self.__root)
        ETC: int = self.create_directory("etc", self.__root)
        HROOT: int = self.create_directory("root", HOME)
        # Add files
        os.chdir("src/data")
        with open("helpmsg.txt") as file:
            self.create_file("help.txt", ETC, file.read())
        with open("greetmsg.txt") as file:
            self.create_file("hello.txt", HROOT, file.read())
        with open("hi.scr") as file:
            self.create_file("hi", BIN, file.read())

    def __initUsers(self) -> None:
        if self.get_user('root') is None:
            self.create_user('root', self.__OPTIONS['rootpassword'])
            return
            
    # Public
    # Users
    def generate_hash(self, password: str, salt: str) -> str:
        return bcrypt.hashpw(password.encode(), salt.encode()).decode()

    # @returns (login: str, password: str, salt: str)
    def get_user(self, login: str) -> tuple[str, str, str] | None:
        cursor = self.__conn.cursor()
        user: tuple[str, str, str] | None = cursor.execute("SELECT login, password, salt FROM users WHERE login = ?", [login]).fetchone()
        cursor.close()
        return user

    def create_user(self, login: str, password: str) -> None:
        if self.get_user(login) is not None:
            raise UserLoginException
        cursor = self.__conn.cursor()
        salt: str = bcrypt.gensalt().decode()
        hashedPassword: str = self.generate_hash(password, salt)
        cursor.execute("INSERT INTO users (login, password, salt) VALUES (?, ?, ?)", [login, hashedPassword, salt])
        self.__conn.commit()
        cursor.close()

    def update_user_password(self, login: str, password: str) -> None:
        if self.get_user(login) is None:
            raise UserLoginException("Missing user by login")
        cursor = self.__conn.cursor()
        salt: str = bcrypt.gensalt().decode() 
        hashedPassword: str = self.generate_hash(password, salt)
        cursor.execute("UPDATE users SET password = ?, salt = ? WHERE login = ?", [hashedPassword, salt, login])
        self.__conn.commit()
        cursor.close()

    def delete_user(self, login: str) -> None:
        if login == 'root':
            raise UserLoginException("Cannot delete root user")
        cursor = self.__conn.cursor()
        cursor.execute("DELETE FROM users WHERE login = ?", [login])
        self.__conn.commit()    
        cursor.close()

    # Filesystem
    def is_file(self, id: int) -> bool:
        cursor = self.__conn.cursor()
        node: tuple[str] | None = cursor.execute("SELECT type FROM nodes WHERE id = ?", [id]).fetchone()
        cursor.close()
        if node is None:
            return False
        return node[0] == "file"
    
    def is_directory(self, id: int) -> bool:
        cursor = self.__conn.cursor()
        node: tuple[str] | None = cursor.execute("SELECT type FROM nodes WHERE id = ?", [id]).fetchone()
        cursor.close()
        if node is None:
            return False
        return node[0] == "directory"
    
    def is_directory_empty(self, id: int) -> bool:
        cursor = self.__conn.cursor()
        node: tuple[int] | None = cursor.execute("SELECT id FROM nodes WHERE parent_id = ? LIMIT 1", [id]).fetchone()
        cursor.close()
        return node is None
    
    def is_root_directory(self, id: int) -> bool:
        return id == self.__root
    
    def is_node_in_directory(self, name: str,  parent_id: int) -> bool:
        cursor = self.__conn.cursor()
        node: tuple[int] | None = cursor.execute("SELECT id FROM nodes WHERE name = ? AND parent_id = ?", [name, parent_id]).fetchone()
        cursor.close()
        return node is not None

    # @returns {int} directory id
    def create_directory(self,  name: str, parent_id: int) -> int:
        if not self.is_directory(parent_id):
            raise NodeTypeException("Tried to create children to not directory parent", parent_id, name)
        if self.is_node_in_directory(name, parent_id):
            raise NodeNameConflictException("This directory already exists", parent_id, name)
        cursor = self.__conn.cursor()
        cursor.execute("INSERT INTO nodes (id, name, type, parent_id) VALUES (NULL, ?, 'directory', ?)", [name, parent_id])
        self.__conn.commit()
        id = cursor.lastrowid
        cursor.close()
        return id
    
    def create_file(self, name: str, parent_id: int, contents: str = None, metadata: str = None) -> int:
        if not self.is_directory(parent_id):
            raise NodeTypeException("Tried to create children to not directory parent", parent_id, name)
        if self.is_node_in_directory(name, parent_id):
            raise NodeNameConflictException("This file already exists", name, parent_id)
        cursor = self.__conn.cursor()
        cursor.execute("INSERT INTO nodes (id, name, type, parent_id) VALUES (NULL, ?, 'file', ?)", [name, parent_id])
        id = cursor.lastrowid
        cursor.execute("INSERT INTO files (node_id, metadata, contents) VALUES (?, ?, ?)", [id, metadata, contents])
        self.__conn.commit()
        cursor.close()
        return id
        
    def delete_directory(self, id: int) -> None:
        if self.is_root_directory(id):
            raise SystemNodeException("Cannot delete root directory", id)
        if not self.is_directory(id):
            raise NodeTypeException("This is not directory", id)
        if not self.is_directory_empty(id):
            raise NodeHasChildrenException("This directory is not empty, use `delete_directory_recusively` to delete not empty directory", id)
        cursor = self.__conn.cursor()
        cursor.execute("DELETE FROM nodes WHERE id = ?", [id])
        self.__conn.commit()
        cursor.close()

    def delete_node(self, id: int) -> None:
        if self.is_root_directory(id):
            raise SystemNodeException("Cannot delete root directory", id)
        if self.is_directory(id):
            for child in self.list_directory(id):
                if child[2] == "directory": # type
                    self.delete_node(child[0])
                elif child[2] == "file":
                    self.delete_file(child[0])
                else:
                    raise NodeTypeException("Unexcepted file type")
            self.delete_directory(id)
        else:
            self.delete_file(id)

    def delete_file(self, id: int) -> None:
        if not self.is_file(id):
            raise NodeTypeException("Not a file provided", id)
        cursor = self.__conn.cursor()
        cursor.execute("DELETE FROM nodes WHERE id = ?", [id])
        cursor.execute("DELETE FROM files WHERE node_id = ?", [id])
        self.__conn.commit()
        cursor.close()

    def prune_system(self) -> None:
        cursor = self.__conn.cursor()
        cursor.execute("DELETE FROM nodes WHERE id NOT IN (?)", [self.__root])
        cursor.execute("DELETE FROM files")
        self.__conn.commit()
        cursor.close()

    def move_node(self, id: int, parent_id: int, name: str | None = None):
        if self.is_root_directory(int):
            raise SystemNodeException("Cannot move root directory", id)
        if not self.is_directory(parent_id): 
            raise NodeTypeException("Tried to move node to not directory parent", id, parent_id)
        cursor = self.__conn.cursor()
        cursor.execute("UPDATE nodes SET parent_id = ? WHERE id = ?", [parent_id, id])
        if name is not None:
            cursor.execute("UPDATE nodes SET name = ? WHERE id = ?", [name, id])
        self.__conn.commit()
        cursor.close()

    def get_file_metadata(self, id: int) ->  str | None:
        if not self.is_file(id):
            raise NodeTypeException("Not a file provided", id)
        cursor = self.__conn.cursor()
        file: tuple[str | None] = cursor.execute("SELECT metadata FROM files WHERE node_id = ?", [id]).fetchone()
        cursor.close()
        return file[0]
    
    def update_file_metadata(self, id: int, metadata: str | None) -> None:
        if not self.is_file(id):
            raise NodeTypeException("Not a file provided", id)
        cursor = self.__conn.cursor()
        cursor.execute("UPDATE files SET metadata = ? WHERE node_id = ?", [metadata, id])
        self.__conn.commit()
        cursor.close()

    def read_file(self, id: int) ->  str | None:
        if not self.is_file(id):
            raise NodeTypeException("Not a file provided", id)
        cursor = self.__conn.cursor()
        file: tuple[str | None] = cursor.execute("SELECT contents FROM files WHERE node_id = ?", [id]).fetchone()
        cursor.close()
        return file[0]
    
    def write_to_file(self, id: int, contents: str | None) -> None:
        if not self.is_file(id):
            raise NodeTypeException("Not a file provided", id)
        cursor = self.__conn.cursor()
        cursor.execute("UPDATE files SET contents = ? WHERE node_id = ?", [contents, id])
        self.__conn.commit()
        cursor.close()

    def append_to_file(self, id: int, contents: str) -> None:
        if not self.is_file(id):
            raise NodeTypeException("Not a file provided", id)
        cursor = self.__conn.cursor()
        cursor.execute("UPDATE files SET contents = contents || ? WHERE node_id = ?", [contents, id])
        self.__conn.commit()
        cursor.close()

    def get_absolute_path(self, id: int) -> str: 
        if self.is_root_directory(id):
            return "/"
        cursor = self.__conn.cursor()
        node: tuple[str, int, str] | None = cursor.execute("SELECT name, parent_id, type FROM nodes WHERE id = ?", [id]).fetchone()
        cursor.close()
        if node is None:
            raise MissingNodeException
        out = self.get_absolute_path(node[1]) + node[0]
        if node[2] == "directory":
            out += "/"
        return  out
    
    # @returns {tuple[name: str, type: str, parent_id: int]}
    def get_node(self, id: int) -> tuple[str, str, int] | None:
        cursor = self.__conn.cursor()
        node: tuple[str, str, int] | None = cursor.execute("SELECT name, type, parent_id FROM nodes WHERE id = ?", [id]).fetchone()
        cursor.close()
        return node
    
    def get_node_path(self, path: str) -> int:
        curr: int = self.__root
        segments: list[str] = path.split("/")
        for seg in segments:
            seg = seg.removeprefix("\"").removesuffix("\"") # Removes "" for whitaspace names
            if not self.is_directory(curr):
                raise NodeTypeException("Wrong path, not directories cannot have children", path, seg)
            match seg:
                case "." | "":
                    continue
                case "..":
                    if self.is_root_directory(curr):
                        continue
                    node = self.get_node(curr)
                    if node is None:
                        raise MissingNodeException
                    curr = node[2] # Set curr = parent_id
                case _:
                    nodes = self.list_directory(curr)
                    for node in nodes: # Searches for node in directory list
                        if seg == node[1]: 
                            curr = node[0]
                            break
                    else:
                        # Node not found in directory list
                        raise MissingNodeException
        return curr
    
    # @returns {list[tuple[id: int, name: str, type: str]]}
    def list_directory(self, id: int) -> list[tuple[int, str, str]]:
        cursor = self.__conn.cursor()
        nodes: list[tuple[int, str, str]] = cursor.execute("SELECT id, name, type FROM nodes WHERE parent_id = ?", [id]).fetchall() 
        cursor.close()
        return nodes
    
    def get_root(self) -> int:
        return self.__root