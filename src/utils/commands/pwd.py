from utils.io import IO

def main(shell, segments: list[str]) -> int:
    IO.write(shell._location)
    return 0