from utils.io import IO
from utils.kernel import MissingNodeException, NodeTypeException, SystemNodeException

def main(shell, segments: list[str]) -> int:
    if(len(segments) < 2):
        IO.write("Missing argument - path")
    path: str = shell._joinPath(segments[1])
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path(path) 
    except (NodeTypeException, MissingNodeException):
        IO.write(f"Invalid path - {path}")
        return 1
    try:
        shell._KERNEL.delete_node(nodeId)
    except SystemNodeException:
        IO.write(f"Cannot delete system directories - {path}")
        return 1
    return 0