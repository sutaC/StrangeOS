from utils import Shell
from utils.io import IO
from utils.kernel import MissingNodeException

def main(shell: Shell, segments: list[str]) -> int:
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path("/etc/help.txt")
    except MissingNodeException:
        IO.write("Cannot find help message", style=IO.Styles.error)
        return 1
    IO.write(shell._KERNEL.read_file(nodeId) or "HELP MISSING")
    return 0
