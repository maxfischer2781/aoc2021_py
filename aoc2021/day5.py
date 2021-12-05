from typing import Iterator
from collections import Counter

FORMAT = """
Part 1: {}
Part 2: {}
"""


def read_lines(in_stream: Iterator[str]):
    """Parse the (x0, y0) -> (x1, y1) format"""
    for line in in_stream:
        pos0, pos1 = [tuple(map(int, pos.split(","))) for pos in line.split("->")]
        yield pos0, pos1


def solve(in_stream):
    lines = list(read_lines(in_stream))
    return overlap_horizontal(lines), overlap_any(lines)


def overlap_horizontal(lines: list[tuple[tuple[int, int], tuple[int, int]]]):
    """Count the fields where horizontal/vertical lines overlap"""
    # The board is probably sparse,
    # so a dict[(x, y), int] is better than a list[list[int]]
    # We use Counter since it is built specifically for keeping counts
    board = Counter()
    for (x0, y0), (x1, y1) in lines:
        if x0 == x1:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                board[x0, y] += 1
        elif y0 == y1:
            for x in range(min(x0, x1), max(x0, x1) + 1):
                board[x, y0] += 1
    # Since indices start at 0, the *index* of the first item smaller than 2
    # is the count of previous items
    for i, (_, count) in enumerate(board.most_common()):
        if count < 2:
            return i
    return len(board)


def point_range(p0, p1):
    """Helper to compute all points from p0 to p1"""
    if p0 < p1:
        return range(p0, p1 + 1)
    else:
        return range(p0, p1 - 1, -1)


def overlap_any(lines: list[tuple[tuple[int, int], tuple[int, int]]]):
    """Count the fields where any lines overlap"""
    board = Counter()
    for (x0, y0), (x1, y1) in lines:
        if x0 == x1:
            for y in point_range(y0, y1):
                board[x0, y] += 1
        elif y0 == y1:
            for x in point_range(x0, x1):
                board[x, y0] += 1
        else:
            for x, y in zip(point_range(x0, x1), point_range(y0, y1)):
                board[x, y] += 1
    for i, (_, count) in enumerate(board.most_common()):
        if count < 2:
            return i
    return len(board)
