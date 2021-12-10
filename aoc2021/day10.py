from typing import Iterator
from io import StringIO


def solve(in_stream: StringIO) -> tuple[object, object]:
    # ): 3 points.
    # ]: 57 points.
    # }: 1197 points.
    # >: 25137 points.
    instructions = [line.strip() for line in in_stream]
    corrupted_cost = {")": 3, "]": 57, "}": 1197, ">": 25137}
    missing_scores = sorted(map(score_missing, find_missing(instructions)))
    return sum(map(corrupted_cost.get, find_corrupted(instructions))), missing_scores[len(missing_scores)//2]


# Symbol pairs are always *nested*: We can have ( [] {} ) but not ( [} {] )
# We can see these as paths, such as ( [] {} ) having the paths (, ([ and ({.
# A stack can represent the current path in which we are. It can only
# - be extended by going one level deeper
# - be shortened by matching the closing symbol for the current level
# - be *corrupt* by matching an *invalid* closing for the current level
# - be *incomplete* by reaching the end of the instruction without closing all levels
def find_corrupted(instructions: list[str]) -> Iterator[str]:
    """Find instructions where level open/close symbols are not the same kind"""
    for line in instructions:
        stack = []
        for symbol in line:
            if symbol in '([{<':
                stack.append(symbol)
            else:
                opening = stack.pop()
                if opening + symbol not in {"()", "[]", "{}", "<>"}:
                    yield symbol


def find_missing(instructions: list[str]) -> Iterator[list[str]]:
    """Find instructions where open symbols are unmatched"""
    for line in instructions:
        stack = []
        for symbol in line:
            if symbol in '([{<':
                stack.append(symbol)
            else:
                opening = stack.pop()
                if opening + symbol not in {"()", "[]", "{}", "<>"}:
                    break
        else:
            yield stack


def score_missing(stack: list[str]) -> int:
    # ): 1 point.
    # ]: 2 points.
    # }: 3 points.
    # >: 4 points.
    missing_cost = {"(": 1, "[": 2, "{": 3, "<": 4}
    total = 0
    for symbol in reversed(stack):
        total *= 5
        total += missing_cost[symbol]
    return total
