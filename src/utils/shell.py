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
        self.__location: str = "/"
        startlocation = self.__joinPath(self.__OPTIONS["startlocation"])
        nodeId: int = None
        try:
            nodeId = kernel.get_node_path(startlocation)
        except (NodeTypeException, MissingNodeException):
            print(Fore.RED, "Could not find starting directory, seting init location to default", Fore.RESET)
        if nodeId is not None:
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
    
    def __pathGetDir(self, path: str) -> str:
        return self.__joinPath(path[:path.rfind("/") + 1])

    def __pathGetBasename(self, path: str) -> str:
        return path[path.rfind("/") + 1:]

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
        if self.__OPTIONS['verbose']: 
            print(Fore.BLACK, "| Segments:", segments, "|", Fore.RESET)
        # Matches instruction

        # TODO: search dynamic

        # match segments[0]:
        #     case "":
        #         def fun():
        #             return 0
        #         return fun
        #     case _:
        #         if segments[0] in self.__SCRIPTS: # Checks saved scripts
        #             def fun():
        #                 return self.runFile(self.__SCRIPTS[segments[0]])
        #             return fun
        #         else:
        #             def fun():
        #                 print(f"Invalid instruction provided - `{instruction}`")
        #                 return 1
        #             return fun


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
        self.__TASKC.addTask(self.__interpretInstruction(instruction))
        self.__TASKC.addTask(self.runInteractive)
                
            