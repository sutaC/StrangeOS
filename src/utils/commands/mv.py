from src.utils.kernel import MissingNodeException, NodeTypeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    if len(segments) < 3:
        print("Missing arguments")
        return 1
    startPath: str = shell.__joinPath(segments[1])
    if shell.__location.startswith(startPath):
        print(f"Cannot move bussy node - {startPath}")
        return 1
    endPath: str = shell.__joinPath(segments[2])
    if shell.__location.startswith(endPath):
        print(f"Invalid path - {endPath}")
        return 1
    nodeId: int
    try:
        nodeId = shell.__KERNEL.get_node_path(startPath)
    except (MissingNodeException, NodeTypeException):
        print(f"Invalid node path - {startPath}")
        return 1
    newParentId: int
    newName: str =  shell.__pathGetBasename(endPath)
    if len(newName) == 0:
        print("Name cannot be empty")
        return 1
    try:
        newParentId = shell.__KERNEL.get_node_path(shell.__pathGetDir(endPath))
        if not shell.__KERNEL.is_directory(newParentId):
            raise MissingNodeException
        if shell.__KERNEL.is_node_in_directory(newName, newParentId):
            raise NodeTypeException
    except (MissingNodeException, NodeTypeException):
        print(f"Invalid path - {endPath}")
        return 1
    try:
        shell.__KERNEL.move_node(nodeId, newParentId, newName)
    except:
        print("Cannot move node")
        return 1
    return 0