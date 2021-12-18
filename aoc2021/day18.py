from io import StringIO
from dataclasses import dataclass
import math
import functools


# We use two separate representations of "Snail Numbers":
# - A flat sequence of nodes of depth-and-value.
# - A nested tree of pairs of trees-or-values.
# The flat sequence is good for addition and reduce, since it allows direct access
# to left/right neighbours across pairs.
# The nested tree is good for magnitude and formatting, since it corresponds to the
# initial left/right pairing.


# I usually prefer `typing.NamedTuple`, since it enforces robust and clean code.
# The algorithms here are more suitable to mutation, though.
@dataclass()
class Node:
    number: int
    depth: int


FlatNumber = list[Node]


TreeNumber = "list[Union[int, TreeNumber]]"


def pairs(sn: FlatNumber) -> TreeNumber:
    depth = 1
    tree = []
    heads = [tree]
    for elem in sn:
        while elem.depth > depth:
            depth += 1
            heads[-1].append([])
            heads.append(heads[-1][-1])
        while elem.depth < depth:
            depth -= 1
            heads.pop()
        heads[-1].append(elem.number)
        while heads and len(heads[-1]) >= 2:
            heads.pop()
            depth -= 1
    return tree


def magnitude(pair: TreeNumber) -> int:
    left, right = (
        part if isinstance(part, int) else magnitude(part)
        for part in pair
    )
    return 3 * left + 2 * right


def reduce(sn: FlatNumber) -> FlatNumber:
    while True:
        # explode
        # It is safe to do a single pass for exploding, provided our input is valid:
        # - The depth of all involved elements is reduced below the threshold, since
        #   `add` only pushes elements just above the threshold. We do not have to
        #   re-visit an element directly after exploding it.
        # - As per implementation, a `list` iterator just traverses the *indices*. As
        #   we demote the i'th element and remove its sibling i+1'th element, the "next"
        #   element to potentially explode moves down to i+1.
        for i, elem in enumerate(sn):
            if elem.depth > 4 and elem.depth == sn[i+1].depth:
                if i > 0:
                    sn[i-1].number += elem.number
                if i < len(sn) - 2:
                    sn[i+2].number += sn[i+1].number
                # Transform [a=x, b=y], c=... to just a=0, c=...; this means the next
                # element to iterate now is the unvisited c and we naturally skip b.
                elem.number = 0
                elem.depth -= 1
                sn.pop(i+1)
        else:
            # split
            for i, elem in enumerate(sn):
                if elem.number > 9:
                    sn.insert(
                        i+1,
                        Node(number=math.ceil(elem.number / 2), depth=elem.depth + 1)
                    )
                    elem.number //= 2
                    elem.depth += 1
                    # resume the loop unless the node needs to explode/split again
                    if elem.depth > 4 or elem.number > 9:
                        break
            else:
                break
    return sn


def add(left: FlatNumber, right: FlatNumber) -> FlatNumber:
    return reduce([
        Node(number=val.number, depth=val.depth + 1)
        for part in (left, right)
        for val in part
    ])


def parse_sn(literal: str) -> FlatNumber:
    sn = []
    depth = 0
    for token in literal:
        if token == ",":
            continue
        elif token == "[":
            depth += 1
        elif token == "]":
            depth -= 1
        else:
            sn.append(Node(number=int(token), depth=depth))
    return sn


def format_sn(sn: FlatNumber) -> str:
    return str(pairs(sn)).replace(" ", "")


def solve(in_stream: StringIO) -> tuple[object, object]:
    numbers = [parse_sn(line.strip()) for line in in_stream]
    return magnitude(pairs(add_all(numbers))), highest_magnitude(numbers)


def add_all(numbers: list[FlatNumber]):
    return functools.reduce(add, numbers)


def highest_magnitude(numbers: list[FlatNumber]):
    highest = 0
    for i in range(len(numbers)):
        for j in range(i+1, len(numbers)):
            mag = magnitude(pairs(add(numbers[i], numbers[j])))
            if mag > highest:
                highest = mag
    return highest
