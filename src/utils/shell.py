import importlib
import os
from types import FunctionType
from colorama import Fore, Style
from .taskcontroller import TaskController
from .kernel import Kernel, MissingNodeException, NodeTypeException
from .options import SysOptions

# Shell lib
class Shell:
    def __init__(self, kernel: Kernel, taskController: TaskController, options: SysOptions) -> None:
        # Init shell
        print(Fore.BLACK, "Shell initialization...", Fore.RESET)
        self.__SCRIPTS: dict = {}
        self.__COMMANDS: dict = {}
        self.__OPTIONS: SysOptions = options
        self._TASKC: TaskController =  taskController
        self._KERNEL: Kernel = kernel
        self._location: str = "/"
        # Sets initial location
        startlocation = self._joinPath(self.__OPTIONS["startlocation"])
        nodeId: int = None
        try:
            nodeId = kernel.get_node_path(startlocation)
        except (NodeTypeException, MissingNodeException):
            print(Fore.RED, "Could not find starting directory, seting init location to default", Fore.RESET)
        if nodeId is not None:
            self._location = startlocation
        print(Fore.BLACK, "Loading shell commands...", Fore.RESET)
        self.__loadCommands()
        print(Fore.BLACK, "Loading shell scripts...", Fore.RESET)
        self.__loadScripts()
        print(Fore.BLACK, f"Shell initialized{Fore.RESET}\n\nWelcome {self.__OPTIONS['username']}!")

    # Private
    def __loadCommands(self) -> None:
        self.__COMMANDS.clear()
        path: str = os.getcwd()
        path = path[:path.rfind("/src") + 4] + "/utils/commands"
        names: list[str] = os.listdir(path)
        for name in names:
            if not name.endswith(".py"):
                continue
            name = name[:-3] # Removes .py
            command: FunctionType
            try:
                module =  importlib.import_module(f"utils.commands.{name}")
                if "main" not in dir(module):
                    raise Exception("Missing main function")
                command: FunctionType = module.main
            except Exception as exc:
                print(Fore.RED, f"* Could not load system command - `{name}`", Fore.RESET)
                if self.__OPTIONS['verbose']:
                    print(repr(exc))
                continue
            print(Fore.GREEN, f"* Successfully loaded system command `{name}`", Fore.RESET)
            self.__COMMANDS[name] = command

    def __loadScripts(self) -> None:
        self.__SCRIPTS.clear()
        binId: int
        try:
            binId = self._KERNEL.get_node_path("/bin")
        except:
            print(Fore.RED, "Could not find bin dir to load scripts", Fore.RESET)
            return
        # (id: int, name: str, type: str)
        scripts = self._KERNEL.list_directory(binId)
        for scr in scripts:                
            scrPath: str
            try:
                scrPath = self._KERNEL.get_absolute_path(scr[0]) # <id>
            except:
                print(Fore.YELLOW, f"Could not load script - `{scr[1]}`", Fore.RESET)
                continue
            self.__SCRIPTS[scr[1]] = scrPath # [<name>] = <path>
            print(Fore.GREEN, f"* Successfully loaded script `{scr[1]}`", Fore.RESET)

    def __interpretInstruction(self, instruction: str) -> FunctionType:
        # Devides instruction to blocks
        instruction = instruction.strip()
        segments: list[str] = []
        seg: str = ""
        i: int = 0
        while i < len(instruction):
            ch = instruction[i]
            match ch:
                case " ":
                    if seg.startswith("\""):
                        seg += " "
                    elif len(seg) > 0:
                        segments.append(seg)
                        seg = ""
                case "\"":
                    if seg.startswith("\""):
                        if len(seg) > 1:
                            segments.append(seg[1:])
                        seg = ""
                    else:    
                        seg += ch
                case "\\":
                    seg += instruction[i+1]
                    i += 1 # Skips next char
                case "#":
                    break
                case _:
                    seg += ch
            i += 1 # Next iteration
        if len(seg) > 0:
            segments.append(seg)
        # Prevents empty segments
        if len(segments) == 0:
            segments.append("")
        # Displays instruction segments for verbose
        if self.__OPTIONS['segments']: 
            print(Fore.BLACK, "| Segments:", segments, "|", Fore.RESET)
        # Matches instruction
        if segments[0] == "": # Empty
            def command():
                return 0
            return command
        if segments[0] in self.__COMMANDS: # System commands
            def command() -> int:
                return self.__COMMANDS[segments[0]](self, segments)
            return command
        if segments[0] in self.__SCRIPTS: # User scripts
            def fun():
                return self.runFile(self.__SCRIPTS[segments[0]])
            return fun
        # Invalid instruction
        def command():
            print(f"Invalid instruction provided - `{instruction}`")
            return 1
        return command

    def __getStyledInput(self) -> str:
        loc = ""        
        if "/home/" in self._location[:6]:
            loc =  "~" + self._location[6:]     
        loc =  self._location
        return f"{Style.BRIGHT}{Fore.GREEN}{self.__OPTIONS['username']}@{self.__OPTIONS['sysname']}{Fore.RESET}:{Fore.BLUE}{loc}{Fore.RESET}${Style.RESET_ALL} "

    # Protected
    def _joinPath(self, destination: str) -> str:
        newDir: str = ""
        if len(destination) == 0 or destination == "~":
            newDir = "/home"
        elif destination[0] == "/":
            newDir = destination
        elif destination[:2] == "~/":
            newDir = "/home/" + destination[2:]
        else:
            newDir += self._location + "/" + destination
        # Path cleaning
        sdirs: list[str] = newDir.split("/")
        i: int = 0
        while 0 <= i < len(sdirs):
            # Sets "" for whitespace dirs
            if sdirs[i].find(" ") > -1:
                sdirs[i] = "\"" + sdirs[i].removeprefix("\"").removesuffix("\"") + "\""
            # Path action
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
        
    def _formatString(self, text: str) -> str:
        return text.replace("\\n", "\n").replace("\\t", "\t")

    def _pathGetDir(self, path: str) -> str:
        return self._joinPath(path[:path.rfind("/") + 1])

    def _pathGetBasename(self, path: str) -> str:
        return path[path.rfind("/") + 1:]

    # Public
    def runFile(self, path: str) -> int:
        nodeId: int
        try:
            nodeId = self._KERNEL.get_node_path(path)
        except (NodeTypeException, MissingNodeException):
            print(f"Node was not found - {path}")
            return 1
        if not self._KERNEL.is_file(nodeId):
            print(f"Not a file was provided - {path}")
            return 1
        file: str = self._KERNEL.read_file(nodeId) or ""
        for line in file.splitlines():
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
                instruction = input(self.__getStyledInput())
            except KeyboardInterrupt:
                print("\nTo exit os type `exit`")
        self._TASKC.addTask(self.__interpretInstruction(instruction))
        self._TASKC.addTask(self.runInteractive)
