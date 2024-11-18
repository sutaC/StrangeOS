from utils.kernel import MissingNodeException, NodeNameConflictException, NodeTypeException

def main(shell, segments: list[str]) -> int:
    if (len(segments) < 2):
        print("Missing argument - path")
        return 1
    PATH = shell._joinPath(segments[1])
    NAME = shell._pathGetBasename(PATH)
    DIR = shell._pathGetDir(PATH)
    try:
        PARENT: int = shell._KERNEL.get_node_path(DIR)
        shell._KERNEL.create_file(NAME, PARENT)
    except (NodeNameConflictException, NodeTypeException, MissingNodeException):
        print(f"Could not create file in that path - `{DIR}` `{NAME}`")
        return 1
    return 0