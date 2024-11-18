from colorama import Fore
from src.utils.kernel import MissingNodeException
from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    nodeId: int
    try:
        nodeId = shell.__KERNEL.get_node_path("/etc/help.txt")
    except MissingNodeException:
        print(Fore.RED, "Cannot find help message", Fore.RESET)
        return 1
    print(shell.__KERNEL.read_file(nodeId) or f"{Fore.RED}HELP MISSING{Fore.RESET}")
    return 0
