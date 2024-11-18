from src.utils.kernel import MissingNodeException, NodeTypeException, SystemNodeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    if(len(segments) < 2):
        print("Missing argument - path")
    path: str = shell.__joinPath(segments[1])
    nodeId: int
    try:
        nodeId = shell.__KERNEL.get_node_path(path) 
    except (NodeTypeException, MissingNodeException):
        print(f"Invalid path - {path}")
        return 1
    try:
        shell.__KERNEL.delete_node(nodeId)
    except SystemNodeException:
        print(f"Cannot delete system directories - {path}")
        return 1
    return 0