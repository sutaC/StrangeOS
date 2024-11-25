from utils.kernel import MissingNodeException, NodeNameConflictException, NodeTypeException
from utils import Shell
from utils.io import IO

def main(shell: Shell, segments: list[str]) -> int:
    if shell._user != "root":
        IO.write("Only root user can delete users")
        return 1
    if len(segments) < 2:
        IO.write("Missing argument - login")
        return 1
    login: str = segments[1] 
    if shell._KERNEL.get_user(login) is None:
        IO.write("User with that login doesn't exist")
        return 1
    shell._KERNEL.delete_user(login)
    try:
        nodeId: int = shell._KERNEL.get_node_path(f"/home/{login}")
        shell._KERNEL.delete_node(nodeId)
    except (MissingNodeException, NodeTypeException):
            IO.write(f"Could not delete user directory in /home/{login}", style=IO.Styles.warning)
    IO.write(f"Deleted user {login}")
    return 0