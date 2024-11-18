def main(shell, segments: list[str]) -> int:
    if len(segments) > 1:
        print(shell._formatString(segments[1]))
    return 0