from utils import Shell
from utils.io import IO

def main(shell: Shell, segments: list[str]) -> int:
    password: str
    try:
        password = input("Password: ")
    except KeyboardInterrupt:
        return 1
    # (login: str, password: str, salt: str)
    user = shell._KERNEL.get_user(shell._user)
    if user is None:
        IO.write("Cannot reach user")
        return 1
    hashed = shell._KERNEL.generate_hash(password, user[2])
    if hashed != user[1]:
        IO.write("Invalid password")
        return 1
    newpassword: str
    try:
        newpassword = input("New password: ")
    except KeyboardInterrupt:
        return 1
    shell._KERNEL.update_user_password(user[0], newpassword)
    IO.write(f"Password updated")
    return 0