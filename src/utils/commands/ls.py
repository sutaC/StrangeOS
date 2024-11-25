from utils import Shell
from utils.io import IO
from utils.kernel import MissingNodeException, NodeTypeException
from colorama import Fore

def main(shell: Shell, segments: list[str]) -> int:
    path = "."
    if(len(segments) > 1):
        path = segments[1]
    path = shell._joinPath(path)
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path(path)
    except (NodeTypeException, MissingNodeException):
        IO.write(f"Could not resolve given path = `{path}`")
        return 1
    if not shell._KERNEL.is_directory(nodeId):
        IO.write(f"Not directories cannot have children - {path}")
        return 1
    # (id: int, name: str, type: str)
    display: list[tuple[int, str, str]] = shell._KERNEL.list_directory(nodeId)
    out: str = ""
    for item in display:
        name = item[1]
        if name.find(" ") > -1:
            name = "\"" + name + "\""
        if item[2] == "directory":
            name = Fore.BLUE + name
        elif item[2] == "file":
            name = Fore.GREEN + name
        out += name + " "
    IO.write(out)
    return 0