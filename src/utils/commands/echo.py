from ..shell import Shell

def main(shell: Shell, segments: list[str]) -> int:
    if len(segments) > 1:
        print(shell.__formatString(segments[1]))
    return 0