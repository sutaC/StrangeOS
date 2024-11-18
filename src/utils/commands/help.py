from utils.kernel import MissingNodeException
from colorama import Fore

def main(shell, segments: list[str]) -> int:
    nodeId: int
    try:
        nodeId = shell._KERNEL.get_node_path("/etc/help.txt")
    except MissingNodeException:
        print(Fore.RED, "Cannot find help message", Fore.RESET)
        return 1
    print(shell._KERNEL.read_file(nodeId) or f"{Fore.RED}HELP MISSING{Fore.RESET}")
    return 0
