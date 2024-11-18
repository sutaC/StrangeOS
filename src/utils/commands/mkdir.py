from src.utils.kernel import MissingNodeException, NodeNameConflictException, NodeTypeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    if (len(segments) < 2):
        print("Missing argument - path")
        return 1
    PATH = shell.__joinPath(segments[1])
    NAME = shell.__pathGetBasename(PATH)
    DIR = shell.__pathGetDir(PATH)
    try:
        PARENT: int = shell.__KERNEL.get_node_path(DIR)
        shell.__KERNEL.create_directory(NAME, PARENT)
    except (NodeNameConflictException, NodeTypeException, MissingNodeException):
        print(f"Could not create directory in that path - `{DIR}` `{NAME}`")
        return 1
    return 0