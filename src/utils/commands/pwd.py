from utils import Shell
from utils.io import IO

def main(shell: Shell, segments: list[str]) -> int:
    IO.write(shell._location)
    return 0