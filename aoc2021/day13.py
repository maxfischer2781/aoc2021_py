from io import StringIO


FORMAT = """
Part 1: {}
Part 2:
-----------------------------
{}
-----------------------------
"""


DOT = tuple[int, int]
FOLD = tuple[str, int]


def read_instructions(in_stream: StringIO) -> tuple[set[DOT], list[FOLD]]:
    points = set()
    for line in map(str.strip, in_stream):
        if not line:
            break
        x, y = map(int, line.split(","))
        points.add((x, y))
    folds = []
    for line in map(str.strip, in_stream):
        [*_, coord], position = line.split("=")
        folds.append((coord, int(position)))
    return points, folds


def solve(in_stream: StringIO) -> tuple[object, object]:
    dots, folds = read_instructions(in_stream)
    return len(fold(dots, folds[0])), format_dots(fold_all(dots, folds))


def fold(dots: set[DOT], by: FOLD) -> set[DOT]:
    coord, position = by
    if coord == "x":
        return {
            dot if dot[0] < position else (dot[0] - 2 * (dot[0] - position), dot[1])
            for dot in dots
        }
    else:
        return {
            dot if dot[1] < position else (dot[0], dot[1] - 2 * (dot[1] - position))
            for dot in dots
        }


def fold_all(dots: set[DOT], instructions: list[FOLD]) -> set[DOT]:
    for instruction in instructions:
        dots = fold(dots, instruction)
    return dots


def format_dots(dots: set[DOT]) -> str:
    result = ""
    prev_x, prev_y = 0, -1
    for x, y in sorted(dots, key=lambda xy: xy[::-1]):
        if y != prev_y:
            result += "\n"
            prev_y, prev_x = y, -1
        result += "  " * (x - prev_x - 1) + "##"
        prev_x = x
    return result
