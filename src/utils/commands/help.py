from utils.io import IO
from utils.kernel import MissingNodeException

def main(shell, segments: list[str]) -> int:
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path("/etc/help.txt")
    except MissingNodeException:
        IO.write("Cannot find help message", style="error")
        return 1
    IO.write(shell._KERNEL.read_file(nodeId) or "HELP MISSING")
    return 0
