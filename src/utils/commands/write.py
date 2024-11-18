from src.utils.kernel import MissingNodeException, NodeTypeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    if len(segments) < 2:
        print("Missing argument - path")
        return 1
    PATH = shell.__joinPath(segments[1])
    contents: str = None
    if len(segments) > 2:
        contents = shell.__formatString(segments[2])
    nodeId: int
    try:
        nodeId = shell.__KERNEL.get_node_path(PATH)
    except (NodeTypeException, MissingNodeException):
        print(f"Invalid path - {PATH}")
        return 1
    if not shell.__KERNEL.is_file(nodeId):
        print(f"Not a file provided - {PATH}")
        return 1
    shell.__KERNEL.write_to_file(nodeId, contents)
    return 0