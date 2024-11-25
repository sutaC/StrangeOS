from utils import Shell
from utils.io import IO
from utils.kernel import MissingNodeException, NodeTypeException

def main(shell: Shell, segments: list[str]) -> int:
    if len(segments) < 3:
        IO.write("Missing arguments")
        return 1
    startPath: str = shell._joinPath(segments[1])
    if shell._location.startswith(startPath):
        IO.write(f"Cannot move bussy node - {startPath}")
        return 1
    endPath: str = shell._joinPath(segments[2])
    if shell._location.startswith(endPath):
        IO.write(f"Invalid path - {endPath}")
        return 1
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path(startPath)
    except (MissingNodeException, NodeTypeException):
        IO.write(f"Invalid node path - {startPath}")
        return 1
    newParentId: int
    newName: str =  shell._pathGetBasename(endPath)
    if len(newName) == 0:
        IO.write("Name cannot be empty")
        return 1
    try:
        newParentId = shell._KERNEL.get_node_path(shell._pathGetDir(endPath))
        if not shell._KERNEL.is_directory(newParentId):
            raise MissingNodeException
        if shell._KERNEL.is_node_in_directory(newName, newParentId):
            raise NodeTypeException
    except (MissingNodeException, NodeTypeException):
        IO.write(f"Invalid path - {endPath}")
        return 1
    try:
        shell._KERNEL.move_node(nodeId, newParentId, newName)
    except:
        IO.write("Cannot move node")
        return 1
    return 0