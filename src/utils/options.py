from .io import IO
from typing import TypedDict
from json import load
import os


class SysOptions(TypedDict):
    sysname: str        # System name
    rootpassword: str   # Password to root user
    dbdir: str          # Directory to filesystem database
    startlocation: str  # Direction where user is after system starts
    verbose: bool       # If true displays verbose error messages
    segments: bool      # If true displays instruction segments

def loadOptions() -> SysOptions | None:
    DIR = os.path.join(os.getcwd(), "options.json")
    if not os.path.isfile(DIR):
        IO.write("Not found options.json")
        return None
    data: SysOptions | None
    with open(DIR) as file:
        data = load(file)
    return data
    
def getDefaultOptions() -> SysOptions:
    opt = SysOptions()
    opt['sysname'] = "system"
    opt['rootpassword'] = ""
    opt['dbdir'] = "filesystem.db"
    opt['startlocation'] = "/"
    opt['verbose'] = False
    opt['segments'] = False
    return opt