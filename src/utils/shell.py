import os
from types import FunctionType
from colorama import Fore, Style
from .taskcontroller import TaskController
from .kernel import Kernel, MissingNodeException, NodeTypeException

# Shell lib
class Shell:
    def __init__(self, kernel: Kernel, taskController: TaskController) -> None:
        print("Shell initialization...")
        self.__SCRIPTS: dict = {}
        self.__TASKC: TaskController =  taskController
        self.__KERNEL: Kernel = kernel

        self.__currNode: int = kernel.get_root()
        self.__location: str = "/"

        # TOADD: users
        self.__USER: str = "user"
        self.__SYSNAME: str = "system"

        print("Loading shell scripts...")
        self.__loadScripts()
        print(f"Shell initialized\n\nWelcome {self.__USER}!")

    # Private
    def __loadScripts(self) -> None:
        pass
        # TODO
        # self.__SCRIPTS.clear()
        # scripts = Instructions.ls("/bin/").split(" ")
        # for scr in scripts:
        #     if len(scr) == 0:
        #         continue
        #     DIR = Instructions.run("/bin/", scr)
        #     if DIR is None:
        #         print(f"* Error while loading script `{scr}`")
        #         continue
        #     print(f"* Successfully loaded script `{scr}`")
        #     self.__SCRIPTS[scr] = DIR

    def __joinPath(self, destination: str) -> str:
        newDir: str = ""
        if len(destination) == 0 or destination == "~":
            newDir = "/home"
        elif destination[0] == "/":
            newDir = destination
        elif destination[:2] == "~/":
            newDir = "/home/" + destination[2:]
        else:
            newDir += self.__location
            if not newDir.endswith("/"):
                newDir += "/"
            newDir += destination
        return newDir

    def __interpretInstruction(self, instruction: str) -> FunctionType:
        segments: list[str] = instruction.split(" ")
        match segments[0]:
            case "help":
                def fun():
                    print("Help msg") # TODO
                    # with open(Instructions.__getDiskDirectory("/system/settings/helpmsg.txt")) as file:
                    #     print(file.read())
                    return 0
                return fun
            case "clear":
                def fun():
                    print("\n" * (os.get_terminal_size().lines + 1))
                    return 0
                return fun
            case "pwd":
                def fun():
                    print(self.__location)
                    return 0
                return fun
            case "ls":
                def fun():
                    # TODO: Add path arg
                    # (id: int, name: str, type: str)
                    display: list[tuple[int, str, str]] = self.__KERNEL.list_directory(self.__currNode)
                    out: str = ""
                    for item in display:
                        name = item[1]
                        if item[2] == "directory":
                            name = Fore.BLUE + name
                        elif item[2] == "file":
                            name = Fore.GREEN + name
                        out += name + " "
                    print(out)
                    return 0
                return fun
            case "cd":
                def fun():
                    destination = ""
                    if len(segments) > 1:
                        destination = segments[1]
                    newDir: str = self.__joinPath(destination)
                    newNode: int
                    try:
                        newNode = self.__KERNEL.get_node_path(newDir)
                    except (MissingNodeException, NodeTypeException):
                        print(f"Invalid path was provided - {destination}")
                        return 1
                    self.__currNode = newNode
                    self.__location = newDir
                    return 0
                return fun
            case "cat":
                def fun():
                    if len(segments) < 2:
                        print("Missing argument - path")
                        return 1
                    FILEPATH: str = self.__joinPath(segments[1])
                    nodeId: int
                    try:
                        nodeId = self.__KERNEL.get_node_path(FILEPATH)
                    except (NodeTypeException, MissingNodeException):
                        print(f"Node was not found - {FILEPATH}")
                        return 1
                    if not self.__KERNEL.is_file(nodeId):
                        print(f"Not a file was provided - {FILEPATH}")
                        return 1
                    print(self.__KERNEL.read_file(nodeId) or "")                    
                    return 0
                return fun
            case "run":
                def fun():
                    if len(segments) < 2:
                        print("Missing argument - path")
                        return 1
                    FILEPATH = self.__joinPath(segments[1])
                    return self.runFile(FILEPATH)
                return fun
            case "echo":
                def fun():
                    print(' '.join(segments[1:]))
                    return 0
                return fun
            case "exit":
                def fun():
                    self.__TASKC.emptyTasks()
                    return 0
                return fun
            case _:
                if segments[0] in self.__SCRIPTS: # Checks saved scripts
                    def fun():
                        return self.runFile(self.__SCRIPTS[segments[0]])
                    return fun
                else:
                    def fun():
                        print(f"Invalid instruction provided - `{instruction}`")
                        return 1
                    return fun


    def __getStyledInput(self) -> str:
        loc = ""        
        if "/home/" in self.__location[:6]:
            loc =  "~" + self.__location[6:]     
        loc =  self.__location
        return f"{Style.BRIGHT}{Fore.GREEN}{self.__USER}@{self.__SYSNAME}{Fore.RESET}:{Fore.BLUE}{loc}{Fore.RESET}${Style.RESET_ALL} "

    # Public
    def runFile(self, path: str) -> int:
        nodeId: int
        try:
            nodeId = self.__KERNEL.get_node_path(path)
        except (NodeTypeException, MissingNodeException):
            print(f"Node was not found - {path}")
            return 1
        if not self.__KERNEL.is_file(nodeId):
            print(f"Not a file was provided - {path}")
            return 1
        file: str = self.__KERNEL.read_file(nodeId) or ""
        for line in file.split("\n"):
            line = line.strip()
            if len(line) == 0:
                continue
            code = self.__interpretInstruction(line)()
            if code != 0:
                return code
        return 0

    def runInteractive(self) -> None:
        instruction: str = None
        while instruction is None:
            try:
                instruction = input(self.__getStyledInput()).strip()
            except KeyboardInterrupt:
                print("\nTo exit os type `exit`")
        self.__TASKC.addTask(self.__interpretInstruction(instruction))
        self.__TASKC.addTask(self.runInteractive)
                
            