from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    if len(segments) < 2:
        print("Missing argument - path")
        return 1
    FILEPATH = shell.__joinPath(segments[1])
    return shell.runFile(FILEPATH)