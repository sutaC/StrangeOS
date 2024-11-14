import os
from colorama import Fore

# Static class lib
class Instructions: 
    # Private
    @staticmethod
    def __cleanDiskLocation(dir: str) -> str:
        sdirs: list[str] = dir.split("/")
        i: int = 0
        while i < len(sdirs):
            match sdirs[i]:
                case "." | "":
                    sdirs.pop(i)
                case  "..":
                    i -= 1
                    sdirs.pop(i)
                    sdirs.pop(i)
                case _:
                    i += 1
        out =  "/".join(sdirs) + "/"
        if len(sdirs) > 0:
            out = "/" + out
        return out


    @staticmethod
    def __getDiskDirectory(location: str) -> str:
        ABSP: str = os.path.dirname(__file__)
        return  os.path.join(ABSP, "..", "..", *location.split("/"))

    @staticmethod
    def __getDiskFilePath(location: str, path: str) -> str:
        fileloc = location
        if len(path.split("/")) > 1:
            fileloc = Instructions.cd(location, os.path.dirname(path))
        DIR: str = Instructions.__getDiskDirectory("/")
        return os.path.join(DIR, *fileloc.split("/"), os.path.basename(path))

    # Public
    @staticmethod
    def help() -> None:
        with open(Instructions.__getDiskDirectory("/system/settings/helpmsg.txt")) as file:
            print(file.read())

    @staticmethod
    def clear() -> None:
        print("\n" * (os.get_terminal_size().lines + 1))

    @staticmethod
    def pwd(location: str) -> None:
        print(location)

    @staticmethod
    def ls(location: str, format: bool = False) -> str:
        # TODO: Add path arg
        DIR: str = Instructions.__getDiskDirectory(location)
        display: list[str] = os.listdir(DIR)
        out: str = ""
        for item in display:
            if format:
                PATH = os.path.join(DIR, item)
                if os.path.isdir(PATH):
                    item = Fore.BLUE + item
                elif os.path.isfile(PATH):
                    item = Fore.GREEN + item
                # Add
            out += item
            if format:
                out += Fore.RESET
            out += " "
        return out

    @staticmethod
    def cd(location: str, destination: str) -> str:
        BASEDIR: str = Instructions.__getDiskDirectory("/")
        newDir: str = ""
        if len(destination) == 0 or destination == "~":
            newDir = "/home"
        elif destination == "/":
            newDir = ""
        elif destination[0] == "/":
            newDir = destination
        elif destination[:2] == "~/":
            newDir = "/home/" + destination[2:]
        else:
            newDir = location + destination
        newDir = Instructions.__cleanDiskLocation(newDir)
        if not os.path.isdir(os.path.join(BASEDIR, *newDir.split("/"))):
            print(f"Invalid path was provided - {destination}")
            return location
        return newDir

    @staticmethod
    def cat(location: str, path: str) -> None:
        FILEPATH = Instructions.__getDiskFilePath(location, path)
        if os.path.isdir(FILEPATH):
            print(f"This is not a file - {path}")
            return
        if not os.access(FILEPATH, os.R_OK):
            print("Cannot access file")
        with open(FILEPATH, "r") as file:
            print(file.read())

    @staticmethod
    def run(location: str, path: str) -> str | None:
        # Return files disk path
        FILEPATH = Instructions.__getDiskFilePath(location, path)
        if os.path.isdir(FILEPATH):
            print(f"This is not a file - {path}")
            return None
        return FILEPATH
        
    @staticmethod
    def echo(args: list[str]) -> None:
        print(' '.join(args))
