import os
from .instructions import  Instructions
from colorama import Fore, Style

# Shell lib
class Shell:
    class Codes:
        OK = 0              # Ok
        ERR = 1             # Runtime error
        INVALID = 400       # Invalid insturction
        NOT_FOUND = 404     # Instruction not found
        CRIT = 500          # Critical error
        EXIT = 518          # System shutdown
        REBOOT = 519        # System reboot

    def __init__(self, user = "user", system: str = "system") -> None:
        print("Shell initialization...")
        self.__location = "/home/"
        self.__USER: str = user
        self.__SYSTEM: str = system
        self.__SCRIPTS: dict = {}
        print("Loading shell scripts...")
        self.__loadScripts()
        print(f"Shell initialized!\nWelcome {self.__USER}!")

    # Private
    def __loadScripts(self) -> None:
        self.__SCRIPTS.clear()
        scripts = Instructions.ls("/bin/").split(" ")
        for scr in scripts:
            if len(scr) == 0:
                continue
            DIR = Instructions.run("/bin/", scr)
            if DIR is None:
                print(f"* Error while loading script `{scr}`")
                continue
            print(f"* Successfully loaded script `{scr}`")
            self.__SCRIPTS[scr] = DIR

    def __checkSegments(self, segments: list[str], minl: int = 1, maxl: int = -1) -> bool:
        if minl < 1:
            raise Exception("Minimal segment count cannot be smaller than 1")
        if maxl < 1:
            maxl = minl
        if len(segments) < minl or len(segments) > maxl:
            print(f"Wrong ammount of arguments was provided ({len(segments)}) - <{minl}, {maxl}> required")
            return True
        return False

    def __performInstruction(self, instruction: str) -> int:
        segments: list[str] = instruction.split(" ")
        # print(segments) # Debugging
        try:
            match segments[0]:
                case "help":
                    if self.__checkSegments(segments):
                        return Shell.Codes.INVALID
                    Instructions.help()
                case "clear":
                    if self.__checkSegments(segments):
                        return Shell.Codes.INVALID
                    Instructions.clear()
                case "pwd":
                    if self.__checkSegments(segments):
                        return Shell.Codes.INVALID
                    Instructions.pwd(self.__location)
                case "ls":
                    if self.__checkSegments(segments):
                        return Shell.Codes.INVALID
                    print(Instructions.ls(self.__location, True))
                case "cd":
                    if self.__checkSegments(segments, 1, 2):
                        return Shell.Codes.INVALID
                    path = ""
                    if len(segments) > 1:
                        path = segments[1]
                    self.__location = Instructions.cd(self.__location, path)
                case "cat":
                    if self.__checkSegments(segments, 2):
                        return Shell.Codes.INVALID
                    Instructions.cat(self.__location, segments[1])
                case "run":
                    if self.__checkSegments(segments, 2):
                        return Shell.Codes.INVALID
                    PTH = Instructions.run(self.__location, segments[1])
                    if PTH is None:
                        return Shell.Codes.ERR
                    return self.runFile(PTH)
                case "echo":
                    Instructions.echo(segments[1:])
                case "reboot":
                    return Shell.Codes.REBOOT
                case "exit":
                    if self.__checkSegments(segments):
                        return Shell.Codes.INVALID
                    print("System closing")
                    return Shell.Codes.EXIT
                case _:
                    if segments[0] in self.__SCRIPTS: # Checks saved scripts
                        self.runFile(self.__SCRIPTS[segments[0]])
                    else:
                        return Shell.Codes.NOT_FOUND
        except Exception as e:
            print(repr(e))
            return Shell.Codes.ERR
        return Shell.Codes.OK

    def __getStyledInput(self) -> str:
        loc = ""        
        if "/home/" in self.__location[:6]:
            loc =  "~" + self.__location[6:]     
        loc =  self.__location
        return f"{Style.BRIGHT}{Fore.GREEN}{self.__USER}@{self.__SYSTEM}{Fore.RESET}:{Fore.BLUE}{loc}{Fore.RESET}${Style.RESET_ALL} "

    # Public
    def runFile(self, path: str) -> None:
        if not os.access(path, os.R_OK):
            print("Cannot access file")
            return Shell.Codes.ERR
        with open(path, "r") as file:
            for line in file:
                line = line.strip()
                if len(line) == 0:
                    continue
                code = self.__performInstruction(line)
                if code != Shell.Codes.OK:
                    return code
        return Shell.Codes.OK

    def runInteractive(self) -> None:
        while True:
            instruction: str = ""
            try:
                instruction = input(self.__getStyledInput()).strip()
            except KeyboardInterrupt:
                print("\nTo exit os type `exit`")
                continue
            code = self.__performInstruction(instruction)
            match code:
                case Shell.Codes.OK:
                    pass
                case Shell.Codes.INVALID:
                    print("Invalid instruction provided")
                case Shell.Codes.NOT_FOUND:
                    print(f"Didn't find matching instruction - `{instruction}`\nType `help` for help.")
                case Shell.Codes.CRIT:
                    print("Critical error courred!")
                    raise Exception("Critical error")
                case Shell.Codes.EXIT:
                    raise Exception("Exit")
                case Shell.Codes.REBOOT:
                    print("Reboot...")
                    return
                case _:
                    print(f"Runtime error ocurred, code - {code}")
                
            