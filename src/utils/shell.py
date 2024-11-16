import os
from types import FunctionType
from colorama import Fore, Style
from .taskcontroller import TaskController
from .kernel import Kernel, MissingNodeException, NodeNameConflictException, NodeTypeException, SystemNodeException
from .options import SysOptions

# Shell lib
class Shell:
    def __init__(self, kernel: Kernel, taskController: TaskController, options: SysOptions) -> None:
        # Init shell
        print(Fore.BLACK, "Shell initialization...", Fore.RESET)
        self.__SCRIPTS: dict = {}
        self.__TASKC: TaskController =  taskController
        self.__KERNEL: Kernel = kernel
        self.__OPTIONS: SysOptions = options
        # Sets initial location
        self.__currNode: int = self.__KERNEL.get_root()
        self.__location: str = "/"
        startlocation = self.__joinPath(self.__OPTIONS["startlocation"])
        nodeId: int = None
        try:
            nodeId = kernel.get_node_path(startlocation)
        except (NodeTypeException, MissingNodeException):
            print(Fore.RED, "Could not find starting directory, seting init location to default", Fore.RESET)
        if nodeId is not None:
            self.__currNode = nodeId
            self.__location = startlocation
        # Loads scripts
        print(Fore.BLACK, "Loading shell scripts...", Fore.RESET)
        self.__loadScripts()
        print(Fore.BLACK, f"Shell initialized{Fore.RESET}\n\nWelcome {self.__OPTIONS['username']}!")

    # Private
    def __loadScripts(self) -> None:
        self.__SCRIPTS.clear()
        binId: int
        try:
            binId = self.__KERNEL.get_node_path("/bin")
        except:
            print(Fore.RED, "Could not find bin dir to load scripts", Fore.RESET)
            return
        # (id: int, name: str, type: str)
        scripts = self.__KERNEL.list_directory(binId)
        for scr in scripts:                
            scrPath: str
            try:
                scrPath = self.__KERNEL.get_absolute_path(scr[0]) # <id>
            except:
                print(Fore.YELLOW, f"Could not load script - `{scr[1]}`", Fore.RESET)
                continue
            self.__SCRIPTS[scr[1]] = scrPath # [<name>] = <path>
            print(Fore.GREEN, f"* Successfully loaded script `{scr[1]}`", Fore.RESET)

    def __formatString(self, text: str) -> str:
        return text.replace("\\n", "\n").replace("\\t", "\t")

    def __joinPath(self, destination: str) -> str:
        newDir: str = ""
        if len(destination) == 0 or destination == "~":
            newDir = "/home"
        elif destination[0] == "/":
            newDir = destination
        elif destination[:2] == "~/":
            newDir = "/home/" + destination[2:]
        else:
            newDir += self.__location + "/" + destination
        # Path cleaning
        sdirs: list[str] = newDir.split("/")
        i: int = 0
        while 0 <= i < len(sdirs):
            match sdirs[i]:
                case "." | "":
                    sdirs.pop(i)
                case  "..":
                    sdirs.pop(i)
                    i -= 1
                    if 0 <= i < len(sdirs):
                        sdirs.pop(i)
                case _:
                    i += 1
        newDir =  "/".join(sdirs)
        if len(sdirs) > 0:
            newDir = "/" + newDir
        return newDir

    def __interpretInstruction(self, instruction: str) -> FunctionType:
        segments: list[str] = instruction.split(" ")
        match segments[0]:
            case "help":
                def fun():
                    nodeId: int
                    try:
                        nodeId = self.__KERNEL.get_node_path("/etc/help.txt")
                    except MissingNodeException:
                        print(Fore.RED, "Cannot find help message", Fore.RESET)
                        return 1
                    print(self.__KERNEL.read_file(nodeId) or f"{Fore.RED}HELP MISSING{Fore.RESET}")
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
                    path = "."
                    if(len(segments) > 1):
                        path = segments[1]
                    path = self.__joinPath(path)
                    nodeId: int
                    try:
                        nodeId = self.__KERNEL.get_node_path(path)
                    except (NodeTypeException, MissingNodeException):
                        print(f"Could not resolve given path = `{path}`")
                        return 1
                    if not self.__KERNEL.is_directory(nodeId):
                        print(f"Not directories cannot have children - {path}")
                        return 1
                    # (id: int, name: str, type: str)
                    display: list[tuple[int, str, str]] = self.__KERNEL.list_directory(nodeId)
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
                    print(self.__formatString(' '.join(segments[1:])))
                    return 0
                return fun
            case "mkdir" | "touch":
                def fun():
                    if (len(segments) < 2):
                        print("Missing argument - path")
                        return 1
                    PATH = self.__joinPath(segments[1]).split("/")
                    NAME = PATH[-1] # Name
                    DIR = '/'.join(PATH[:-1]) 
                    try:
                        PARENT: int = self.__KERNEL.get_node_path(DIR)
                        if segments[0] == "mkdir":
                            self.__KERNEL.create_directory(NAME, PARENT)
                        elif segments[0] == "touch":
                            self.__KERNEL.create_file(NAME, PARENT)
                    except (NodeNameConflictException, NodeTypeException, MissingNodeException):
                        print(f"Could not create node in that path - `{DIR}` `{NAME}`")
                        return 1
                    return 0
                return fun
            case "rm":
                def fun():
                    if(len(segments) < 2):
                        print("Missing argument - path")
                    path: str = self.__joinPath(segments[1])
                    nodeId: int
                    try:
                        nodeId = self.__KERNEL.get_node_path(path) 
                    except (NodeTypeException, MissingNodeException):
                        print(f"Invalid path - {path}")
                        return 1
                    try:
                        self.__KERNEL.delete_node(nodeId)
                    except SystemNodeException:
                        print(f"Cannot delete system directories - {path}")
                        return 1
                    return 0
                return fun
            case "write" | "append":
                def fun():
                    if len(segments) < 2:
                        print("Missing argument - path")
                        return 1
                    PATH = self.__joinPath(segments[1])
                    contents: str = self.__formatString(' '.join(segments[2:]))
                    nodeId: int
                    try:
                        nodeId = self.__KERNEL.get_node_path(PATH)
                    except (NodeTypeException, MissingNodeException):
                        print(f"Invalid path - {PATH}")
                        return 1
                    if not self.__KERNEL.is_file(nodeId):
                        print(f"Not a file provided - {PATH}")
                        return 1
                    if segments[0] == "write":
                        self.__KERNEL.write_to_file(nodeId, contents)
                    elif segments[0] == "append":
                        self.__KERNEL.append_to_file(nodeId, "\n" + contents)
                    return 0
                return fun
            case "exit":
                def fun():
                    self.__TASKC.emptyTasks()
                    return 0
                return fun
            case "" | "#":
                def fun():
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
        return f"{Style.BRIGHT}{Fore.GREEN}{self.__OPTIONS['username']}@{self.__OPTIONS['sysname']}{Fore.RESET}:{Fore.BLUE}{loc}{Fore.RESET}${Style.RESET_ALL} "

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
                
            