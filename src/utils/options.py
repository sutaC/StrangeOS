from typing import TypedDict
from json import load
import os

class SysOptions(TypedDict):
    sysname: str    # System name
    username: str   # User name
    dbdir: str      # Directory to filesystem database
    startlocation: str
    verbose: bool   # If true displays verbose error messages

def loadOptions() -> SysOptions | None:
    DIR = os.path.join(os.getcwd(), "options.json")
    if not os.path.isfile(DIR):
        print("Not found options.json")
        return None
    data: SysOptions | None
    with open(DIR) as file:
        data = load(file)
    return data
    
def getDefaultOptions() -> SysOptions:
    opt = SysOptions()
    opt['sysname'] = "system"
    opt['username'] = "user"
    opt['dbdir'] = "filesystem.db"
    opt["startlocation"] = "/"
    opt['verbose'] = False
    return opt