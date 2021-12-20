from io import StringIO
from typing import Iterable


# The standard approach for sparse Black/White images is a set of "switched on" pixels
# This task has a complication:
# - the image is infinite in size
# - the "padding" to infinity may be either black or white!
# We use a slightly more complex layout, combining the set with a flag to indicate
# whether the "switched on" pixels represent white or black.
IMAGE_MASK = tuple[set[tuple[int, int]], bool]


def read_input(in_stream: StringIO) -> tuple[str, IMAGE_MASK]:
    """Read the task or example input"""
    # the task has the key on one line, but the example spans several
    key = []
    for line in map(str.strip, in_stream):
        if not line:
            break
        key.append(line)
    image = {
        (row, column)
        for row, line in enumerate(map(str.strip, in_stream))
        for column, pixel in enumerate(line)
        if pixel == "#"
    }
    return "".join(key), (image, False)


def solve(in_stream: StringIO) -> tuple[object, object]:
    key, image = read_input(in_stream)
    for _ in range(2):
        image = enhance(image, key)
    long_image = image
    for _ in range(48):
        long_image = enhance(long_image, key)
    return len(image[0]), len(long_image[0])


def neighbours(row, column) -> Iterable[tuple[int, int]]:
    """Compute the neighbour positions of (row, column)"""
    return [
        (row + row_offset, column + column_offset)
        for row_offset in (-1, 0, 1)
        for column_offset in (-1, 0, 1)
    ]


def enhance(image: IMAGE_MASK, key: str) -> IMAGE_MASK:
    """Apply one enhancement step to `image` using `key`"""
    assert key[0] == "." or key[0] != key[1], "key must be stable modulo 2"
    mask, inverted = image
    new_mask, new_inverted = set(), inverted ^ (key[0] == "#")
    (min_row, max_row), (min_column, max_column) = bounds(image)
    for row in range(min_row-2, max_row+3):
        for column in range(min_column - 2, max_column + 3):
            index = int(
                ''.join('1' if nb in mask else '0' for nb in neighbours(row, column)),
                2,
            )
            if inverted:
                index ^= 0b111111111
            if key[index] == ("#" if not new_inverted else "."):
                new_mask.add((row, column))
    return new_mask, new_inverted


def bounds(image: IMAGE_MASK) -> tuple[tuple[int, int], tuple[int, int]]:
    # (min_row, max_row), (min_column, max_column)
    rows = sorted(row for row, _ in image[0])
    columns = sorted(column for _, column in image[0])
    return (rows[0], rows[-1]), (columns[0], columns[-1])
