from src.utils.kernel import MissingNodeException, NodeTypeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    if len(segments) < 3:
        print("Missing arguments")
        return 1
    startPath: str = shell.__joinPath(segments[1])
    endPath: str = shell.__joinPath(segments[2])
    # Copy from node
    nodeId: int
    # (name: str, type: str, parent_id: int)
    node: tuple[str, str, int]
    try:
        nodeId = shell.__KERNEL.get_node_path(startPath)
        node = shell.__KERNEL.get_node(nodeId)
    except (MissingNodeException, NodeTypeException):
        print(f"Invalid node path - {startPath}")
        return 1
    parentId: int
    name: str =  shell.__pathGetBasename(endPath)
    if len(name) == 0:
        print("Name cannot be empty")
        return 1
    try:
        parentId = shell.__KERNEL.get_node_path(shell.__pathGetDir(endPath))
        if not shell.__KERNEL.is_directory(parentId):
            raise MissingNodeException
        if shell.__KERNEL.is_node_in_directory(name, parentId):
            raise NodeTypeException
    except (MissingNodeException, NodeTypeException):
        print(f"Invalid path - {endPath}")
        return 1
    try:
        if node[1] == "file":
            contents = shell.__KERNEL.read_file(nodeId)
            metadata = shell.__KERNEL.get_file_metadata(nodeId)
            shell.__KERNEL.create_file(name, parentId, contents, metadata)
        elif node[1] == "directory":
            shell.__KERNEL.create_directory(name, parentId)
    except:
        print("Cannot copy node")
        return 1
    return 0
