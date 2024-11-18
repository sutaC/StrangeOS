from utils.io import IO
from utils.kernel import MissingNodeException, NodeTypeException

def main(shell, segments: list[str]) -> int:
    destination = ""
    if len(segments) > 1:
        destination = segments[1]
    newDir: str = shell._joinPath(destination)
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path(newDir)
    except (MissingNodeException, NodeTypeException):
        IO.write(f"Invalid path was provided - {newDir}")
        return 1
    if not shell._KERNEL.is_directory(nodeId):
        IO.write(f"Cannot enter not a directory - {newDir}")
        return 1
    shell._location = newDir
    return 0