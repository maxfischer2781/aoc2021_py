from io import StringIO

FORMAT = """
Part 1: {}
Part 2: {}
"""


def solve(in_stream: StringIO):
    start_positions = list(map(int, in_stream.read().split(",")))
    return least_linear_cost(start_positions), least_cost(
        start_positions, triangular_cost
    )


def linear_cost(center, positions):
    return sum(abs(pos - center) for pos in positions)


def least_linear_cost(positions: list[int]):
    # The median minimises the sum of absolute distance
    median = sorted(positions)[len(positions) // 2]
    return linear_cost(median, positions)


# This is a brute-force algorithm
# We calculate the linear/triangular cost for *every* possible position and pick the
# best.
def triangular_cost(center, positions):
    return sum((n := abs(pos - center)) * (n + 1) // 2 for pos in positions)


# We could probably do this more efficiently using bisection or descent...
def least_cost(start_positions: list[int], cost):
    return min(
        map(
            lambda center: cost(center, start_positions),
            range(min(start_positions), max(start_positions)),
        )
    )
