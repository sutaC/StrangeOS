from utils.kernel import MissingNodeException, NodeTypeException

def main(shell, segments: list[str]) -> int:
    if len(segments) < 2:
        print("Missing argument - path")
        return 1
    PATH = shell._joinPath(segments[1])
    contents: str = None
    if len(segments) > 2:
        contents = shell._formatString(segments[2])
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path(PATH)
    except (NodeTypeException, MissingNodeException):
        print(f"Invalid path - {PATH}")
        return 1
    if not shell._KERNEL.is_file(nodeId):
        print(f"Not a file provided - {PATH}")
        return 1
    shell._KERNEL.write_to_file(nodeId, contents)
    return 0