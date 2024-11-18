from ..shell import Shell
from os import get_terminal_size

def main(shell: Shell, segments: list[str]) -> int:
    print("\n" * (get_terminal_size().lines + 1))
    return 0