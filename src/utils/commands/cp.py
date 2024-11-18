from utils.io import IO
from utils.kernel import MissingNodeException, NodeTypeException

def main(shell, segments: list[str]) -> int:
    if len(segments) < 3:
        IO.write("Missing arguments")
        return 1
    startPath: str = shell._joinPath(segments[1])
    endPath: str = shell._joinPath(segments[2])
    # Copy from node
    nodeId: int
    # (name: str, type: str, parent_id: int)
    node: tuple[str, str, int]
    try:
        nodeId = shell._KERNEL.get_node_path(startPath)
        node = shell._KERNEL.get_node(nodeId)
    except (MissingNodeException, NodeTypeException):
        IO.write(f"Invalid node path - {startPath}")
        return 1
    parentId: int
    name: str =  shell._pathGetBasename(endPath)
    if len(name) == 0:
        IO.write("Name cannot be empty")
        return 1
    try:
        parentId = shell._KERNEL.get_node_path(shell._pathGetDir(endPath))
        if not shell._KERNEL.is_directory(parentId):
            raise MissingNodeException
        if shell._KERNEL.is_node_in_directory(name, parentId):
            raise NodeTypeException
    except (MissingNodeException, NodeTypeException):
        IO.write(f"Invalid path - {endPath}")
        return 1
    try:
        if node[1] == "file":
            contents = shell._KERNEL.read_file(nodeId)
            metadata = shell._KERNEL.get_file_metadata(nodeId)
            shell._KERNEL.create_file(name, parentId, contents, metadata)
        elif node[1] == "directory":
            shell._KERNEL.create_directory(name, parentId)
    except:
        IO.write("Cannot copy node")
        return 1
    return 0
