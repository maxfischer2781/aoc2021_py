from io import StringIO
from dataclasses import dataclass
import math


# We use two separate representations of "Snail Numbers":
# - A flat sequence of node with depth.
# - A nested tree of pairs.
# The flat sequence is good for addition and reduce, since it allows direct access
# to left/right neighbours across pairs.
# The nested tree is good for magnitude and formatting, since it corresponds to the
# initial left/right pairing.


@dataclass()
class Value:
    number: int
    depth: int


SnailNumber = list[Value]


def add(left: SnailNumber, right: SnailNumber) -> SnailNumber:
    return [
        Value(number=val.number, depth=val.depth + 1)
        for part in (left, right)
        for val in part
    ]


TreeNumber = "list[Union[int, TreeNumber]]"


def pairs(sn: SnailNumber) -> TreeNumber:
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


def reduce(sn: SnailNumber) -> SnailNumber:
    while True:
        # explode
        for i, elem in enumerate(sn):
            if elem.depth > 4 and elem.depth == sn[i+1].depth:
                if i > 0:
                    sn[i-1].number += elem.number
                if i < len(sn) - 2:
                    sn[i+2].number += sn[i+1].number
                elem.number = 0
                elem.depth -= 1
                sn.pop(i+1)
                break
        else:
            # split
            for i, elem in enumerate(sn):
                if elem.number > 9:
                    sn.insert(
                        i+1,
                        Value(number=math.ceil(elem.number / 2), depth=elem.depth+1)
                    )
                    elem.number //= 2
                    elem.depth += 1
                    break
            else:
                break
    return sn


def parse_sn(literal: str) -> SnailNumber:
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
            sn.append(Value(number=int(token), depth=depth))
    return sn


def format_sn(sn: SnailNumber) -> str:
    return str(pairs(sn)).replace(" ", "")


def solve(in_stream: StringIO) -> tuple[object, object]:
    numbers = [parse_sn(line.strip()) for line in in_stream]
    return magnitude(pairs(add_all(numbers))), highest_magnitude(numbers)


def add_all(numbers: list[SnailNumber]):
    iterator = iter(numbers)
    current = next(iterator)
    for number in iterator:
        current = reduce(add(current, number))
    return current


def highest_magnitude(numbers: list[SnailNumber]):
    highest = 0
    for i in range(len(numbers)):
        for j in range(i+1, len(numbers)):
            mag = magnitude(pairs(reduce(add(numbers[i], numbers[j]))))
            if mag > highest:
                highest = mag
    return highest
