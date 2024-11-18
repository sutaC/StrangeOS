from src.utils.kernel import MissingNodeException, NodeTypeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    destination = ""
    if len(segments) > 1:
        destination = segments[1]
    newDir: str = shell.__joinPath(destination)
    nodeId: int
    try:
        nodeId = shell.__KERNEL.get_node_path(newDir)
    except (MissingNodeException, NodeTypeException):
        print(f"Invalid path was provided - {newDir}")
        return 1
    if not shell.__KERNEL.is_directory(nodeId):
        print(f"Cannot enter not a directory - {newDir}")
        return 1
    shell.__location = newDir
    return 0