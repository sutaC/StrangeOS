from utils.io import IO

def main(shell, segments: list[str]) -> int:
    if len(segments) > 1:
        IO.write(shell._formatString(segments[1]))
    return 0