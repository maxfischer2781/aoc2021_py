from typing import Iterable, Any
from io import StringIO


ADJACENCY_MAP = dict[str, frozenset[str]]
PATH = tuple[str, ...]
SEEN = frozenset[str, ...]


def solve(in_stream: StringIO) -> tuple[object, object]:
    adjacency = read(in_stream)
    return count(find_unique_paths(adjacency, ("start",), frozenset())), count(
        find_single_paths(adjacency, ("start",), frozenset())
    )


def read(in_stream: StringIO) -> ADJACENCY_MAP:
    """Read the task input to an adjacency map of source and connected caves"""
    adjacency = {}
    for line in map(str.strip, in_stream):
        left, right = line.split("-")
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    return {parent: frozenset(adjacent) for parent, adjacent in adjacency.items()}


def count(obj: Iterable[Any]) -> int:
    """Provide the length of an iterator destructively"""
    return sum(1 for _ in obj)


# This is a straightforward path search:
# - recursively visit all possible connections
# - avoid re-visiting a small cave (twice) by keeping a set of visited small caves
#   - we could use the path for determining visited caves – but a set should be faster
# - when we hit the "end", the path is valid and we may yield it
def find_unique_paths(
    caves: ADJACENCY_MAP, path: PATH, seen_small: SEEN
) -> Iterable[PATH]:
    """Find the paths with unique visits to any small cave"""
    current = path[-1]
    if current == "end":
        yield path
    else:
        if current.islower():
            seen_small = seen_small | {current}
        for child in caves[current]:
            if child not in seen_small and child != "start":
                yield from find_unique_paths(caves, path + (child,), seen_small)


def find_single_paths(
    caves: ADJACENCY_MAP, path: PATH, seen_small: SEEN
) -> Iterable[PATH]:
    """Find the paths with unique visits to any small cave but at most one"""
    current = path[-1]
    if current == "end":
        yield path
    else:
        if current.islower():
            seen_small = seen_small | {current}
        for child in caves[current]:
            if child == "start":
                continue
            elif child not in seen_small:
                yield from find_single_paths(caves, path + (child,), seen_small)
            else:
                # not re-visiting a cave is the part 1 task
                yield from find_unique_paths(caves, path + (child,), seen_small)
