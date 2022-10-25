# Task: Given some binary numbers,
# a) for each digit-position find the most common digit, and
# b) similarly to a) but discard numbers according to a specific scheme.
from typing import Optional


def solve(in_stream):
    data = [line.strip() for line in in_stream]
    digits = len(data[0])
    # It is sufficient to calculate the gamma_rate *or* the epsilon rate.
    # By definition, one is the two-complement of the other.
    gamma_rate = most_common_binary(data)
    oxygen, co2 = stepwise_binary(data)
    return gamma_rate * (2 ** digits - 1 - gamma_rate), oxygen * co2


def most_common_binary(report: list[str]):
    """Find the most common binary digit at each position"""
    # We use a running total of "1 count - 0 count" for each digit
    # If we have "110...", "101...", "001..." then count for digit 0 is 2-1>0,
    # for digit 1 is 1-2<0, and so on.
    # If the result is positive there were more 1s, otherwise there were more 0s.
    counts = [0] * len(report[0])
    for line in report:
        counts = [
            prev + 1 if digit == "1" else prev - 1 for prev, digit in zip(counts, line)
        ]
    return int(
        "".join("1" if count > 0 else "0" for count in counts),
        2,
    )


# Alternative for part a:
# We could zip then entire input so that instead of
#   number 1: digit 1, digit 2, …, number2: …
# we get
#   digit 1: number 1, number 2, …, digit 2: …
# instead. This would allow to directly sum the 1s for each digit.
# If there are more 1s than half the lines, 1 is most common for that digit.


class BinaryPrefixTree:
    """
    Utility data structure to track the number of specific prefixes

    The set of numbers ['10', '11', '01', '01', '11'] will be represented as the tree:

            [2, 3]
           /     \
        [0, 2] [1, 2]

    After filling the tree with many numbers, we can efficiently select the least/most
    common digit pattern.
    """
    __slots__ = ("counts", "children")

    def __init__(self, depth=0):
        # Since our digits are 0 or 1, we can use plain lists of length two
        # (i.e. indexed by 0 or 1) to store the information of each tree node.
        self.counts = [0, 0]
        self.children: Optional[tuple[BinaryPrefixTree, BinaryPrefixTree]] = (
            (BinaryPrefixTree(depth - 1), BinaryPrefixTree(depth - 1))
            if depth > 1
            else None
        )

    def add(self, binary: str):
        """Mutate the tree to add the new `binary` number"""
        head = int(binary[0])
        self.counts[head] += 1
        if self.children is not None:
            self.children[head].add(binary[1:])

    def most_common(self, largest: bool) -> str:
        """
        Provide the most/least common binary sequence stored in the tree

        If `largest` is True, use the *most common* bit criteria.
        Otherwise, use the *least common* bit criteria.
        """
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


def stepwise_binary(report: list[str]):
    # Use a BinaryPrefixTree to build a single representation of
    # most/least common sequences in a single pass
    tree = BinaryPrefixTree(depth=len(report[0]))
    for line in report:
        tree.add(line)
    return int(tree.most_common(True), 2), int(tree.most_common(False), 2)
