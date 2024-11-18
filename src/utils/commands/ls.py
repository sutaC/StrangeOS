from colorama import Fore
from src.utils.kernel import MissingNodeException, NodeTypeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    path = "."
    if(len(segments) > 1):
        path = segments[1]
    path = shell.__joinPath(path)
    nodeId: int
    try:
        nodeId = shell.__KERNEL.get_node_path(path)
    except (NodeTypeException, MissingNodeException):
        print(f"Could not resolve given path = `{path}`")
        return 1
    if not shell.__KERNEL.is_directory(nodeId):
        print(f"Not directories cannot have children - {path}")
        return 1
    # (id: int, name: str, type: str)
    display: list[tuple[int, str, str]] = shell.__KERNEL.list_directory(nodeId)
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
    print(out)
    return 0