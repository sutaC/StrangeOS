from utils import Shell
from utils.io import IO
from utils.kernel import MissingNodeException, NodeTypeException

def main(shell: Shell, segments: list[str]) -> int:
    if len(segments) < 2:
        IO.write("Missing argument - path")
        return 1
    FILEPATH: str = shell._joinPath(segments[1])
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path(FILEPATH)
    except (NodeTypeException, MissingNodeException):
        IO.write(f"Node was not found - {FILEPATH}")
        return 1
    if not shell._KERNEL.is_file(nodeId):
        IO.write(f"Not a file was provided - {FILEPATH}")
        return 1
    IO.write(shell._KERNEL.read_file(nodeId) or "")                    
    return 0