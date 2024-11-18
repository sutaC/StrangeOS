from os import get_terminal_size

def main(shell, segments: list[str]) -> int:
    print("\n" * (get_terminal_size().lines + 1))
    return 0