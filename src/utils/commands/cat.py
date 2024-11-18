from utils.kernel import MissingNodeException, NodeTypeException

def main(shell, segments: list[str]) -> int:
    if len(segments) < 2:
        print("Missing argument - path")
        return 1
    FILEPATH: str = shell._joinPath(segments[1])
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path(FILEPATH)
    except (NodeTypeException, MissingNodeException):
        print(f"Node was not found - {FILEPATH}")
        return 1
    if not shell._KERNEL.is_file(nodeId):
        print(f"Not a file was provided - {FILEPATH}")
        return 1
    print(shell._KERNEL.read_file(nodeId) or "")                    
    return 0