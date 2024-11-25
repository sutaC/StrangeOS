from utils import Shell
from utils.io import IO
from utils.kernel import MissingNodeException, NodeNameConflictException, NodeTypeException

def main(shell: Shell, segments: list[str]) -> int:
    if (len(segments) < 2):
        IO.write("Missing argument - path")
        return 1
    PATH = shell._joinPath(segments[1])
    NAME = shell._pathGetBasename(PATH)
    DIR = shell._pathGetDir(PATH)
    try:
        PARENT: int = shell._KERNEL.get_node_path(DIR)
        shell._KERNEL.create_directory(NAME, PARENT)
    except (NodeNameConflictException, NodeTypeException, MissingNodeException):
        IO.write(f"Could not create node in that path - `{DIR}` `{NAME}`")
        return 1
    return 0