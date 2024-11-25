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
            print("Invalid login")
            continue
        break
    for tries in range(3):
        password: str
        try:
            password = input("Password: ")
        except KeyboardInterrupt:
            return 1
        hashed: str = shell._KERNEL.generate_hash(password, user[2])
        if hashed == user[1]:
            print(f"Logged in as {user[0]}")
            shell._user = user[0]
            return 0
        print("Invalid password")
    print("Login failed")
    return 1