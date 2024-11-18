from utils.io import IO

def main(shell, segments: list[str]) -> int:
    if len(segments) < 2:
        IO.write("Missing argument - path")
        return 1
    FILEPATH = shell._joinPath(segments[1])
    return shell.runFile(FILEPATH)