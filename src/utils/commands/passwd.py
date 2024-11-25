from utils import Shell
from utils.io import IO
import getpass

def main(shell: Shell, segments: list[str]) -> int:
    login: str = shell._user
    if len(segments) > 1:
        if shell._user != "root":
            IO.write("Only root user can change others passwords")
            return 1
        login = segments[1]
    # (login: str, password: str, salt: str)
    user = shell._KERNEL.get_user(login)
    if user is None:
        IO.write(f"Cannot find user {login}")
        return 1
    IO.write(f"Changing password for {login}")
    newpassword: str
    try:
        newpassword = getpass.getpass("New password: ")
    except KeyboardInterrupt:
        return 1
    rnewpassword: str 
    try:
        rnewpassword = getpass.getpass("Repeat password: ")
    except KeyboardInterrupt:
        return 1
    if newpassword != rnewpassword:
        IO.write("Password and repeat password doesn't match")
        return 1
    shell._KERNEL.update_user_password(user[0], newpassword)
    IO.write(f"Password updated")
    return 0