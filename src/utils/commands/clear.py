from utils import Shell
from os import get_terminal_size
from utils.io import IO

def main(shell: Shell, segments: list[str]) -> int:
    IO.write("\n" * (get_terminal_size().lines + 1))
    return 0