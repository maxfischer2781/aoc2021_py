from typing import Optional

FORMAT = """
Part 1: {}
Part 2: {}
"""


class BinaryPrefixTree:
    __slots__ = ("counts", "children")

    def __init__(self, depth=0):
        self.counts = [0, 0]
        self.children: Optional[tuple[BinaryPrefixTree, BinaryPrefixTree]] = (
            (BinaryPrefixTree(depth - 1), BinaryPrefixTree(depth - 1))
            if depth > 1
            else None
        )

    def add(self, binary: str):
        head = int(binary[0])
        self.counts[head] += 1
        if self.children is not None:
            self.children[head].add(binary[1:])

    def most_common(self, largest: bool) -> str:
        if largest:
            head = 1 if self.counts[1] >= self.counts[0] else 0
        else:
            # Even if there was no item there is always a child tree at count 0
            # We need to exclude this when looking for the smaller count
            head = (
                0
                if (self.counts[0] and self.counts[0] <= self.counts[1])
                or not self.counts[1]
                else 1
            )
        if self.children is not None:
            return str(head) + self.children[head].most_common(largest)
        else:
            return str(head)


def solve(in_stream):
    data = [line.strip() for line in in_stream]
    digits = len(data[0])
    gamma_rate = most_common_binary(data)
    oxygen, co2 = stepwise_binary(data)
    return gamma_rate * (2 ** digits - 1 - gamma_rate), oxygen * co2


def most_common_binary(report: list[str]):
    """Find the most common binary digit at each position"""
    # We use a running total of "1 count - 0 count"
    # If the result is positive there were more 1s, otherwise there were more 0s
    counts = [0] * len(report[0])
    for line in report:
        counts = [
            prev + 1 if digit == "1" else prev - 1 for prev, digit in zip(counts, line)
        ]
    return int(
        "".join("1" if count > 0 else "0" for count in counts),
        2,
    )


def stepwise_binary(report: list[str]):
    # Use a BinaryPrefixTree to build a single representation of
    # most/least common sequences in a single pass
    tree = BinaryPrefixTree(depth=len(report[0]))
    for line in report:
        tree.add(line)
    return int(tree.most_common(True), 2), int(tree.most_common(False), 2)
