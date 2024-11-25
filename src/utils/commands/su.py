import getpass
from utils.io import IO
from utils import Shell

def main(shell: Shell, segments: list[str]) -> int:
    # (login: str, password: str, salt: str)
    user: tuple[str, str, str] | None
    while True:
        login: str
        try:
            login = input("Login: ")
        except KeyboardInterrupt:
            return 1
        user = shell._KERNEL.get_user(login)
        if user is None:
            IO.write("Invalid login")
            continue
        break
    for tries in range(3):
        password: str
        try:
            password = getpass.getpass("Password: ")
        except KeyboardInterrupt:
            return 1
        hashed: str = shell._KERNEL.generate_hash(password, user[2])
        if hashed == user[1]:
            IO.write(f"Logged in as {user[0]}")
            shell._user = user[0] # Login
            shell._setInitialLocation()
            return 0
        IO.write("Invalid password")
    IO.write("Login failed")
    return 1