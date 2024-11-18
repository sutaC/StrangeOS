from src.utils.kernel import MissingNodeException, NodeTypeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    if len(segments) < 2:
        print("Missing argument - path")
        return 1
    FILEPATH: str = shell.__joinPath(segments[1])
    nodeId: int
    try:
        nodeId = shell.__KERNEL.get_node_path(FILEPATH)
    except (NodeTypeException, MissingNodeException):
        print(f"Node was not found - {FILEPATH}")
        return 1
    if not shell.__KERNEL.is_file(nodeId):
        print(f"Not a file was provided - {FILEPATH}")
        return 1
    print(shell.__KERNEL.read_file(nodeId) or "")                    
    return 0