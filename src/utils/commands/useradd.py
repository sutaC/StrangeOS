from utils.kernel import NodeNameConflictException
from utils import Shell
from utils.io import IO

def main(shell: Shell, segments: list[str]) -> int:
    if shell._user != "root":
        IO.write("Only root user can add new users")
        return 1
    if len(segments) < 2:
        IO.write("Missing argument - login")
        return 1
    login: str = segments[1] 
    if shell._KERNEL.get_user(login) is not None:
        IO.write("User with that login already exists")
        return 1
    password: str = ""
    if len(segments) > 2:
        password = segments[2]
    shell._KERNEL.create_user(login, password)
    try:
        shell._KERNEL.create_directory(login, shell._KERNEL.get_node_path("/home"))
    except NodeNameConflictException:
            IO.write(f"Could not create user directory in /home/{login}", style=IO.Styles.warning)
    IO.write(f"Created user {login}")
    return 0