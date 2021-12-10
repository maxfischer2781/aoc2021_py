from io import StringIO
import math

FORMAT = """
Part 1: {}
Part 2: {}
"""


def solve(in_stream: StringIO):
    start_positions = list(map(int, in_stream.read().split(",")))
    return least_linear_cost(start_positions), least_triangular_cost(start_positions)


def linear_cost(center, positions):
    return sum(abs(pos - center) for pos in positions)


def least_linear_cost(positions: list[int]):
    # The median minimises the sum of absolute distance
    # It is the middle position (len(positions) // 2) of the sorted values.
    median = sorted(positions)[len(positions) // 2]
    return linear_cost(median, positions)


def triangular_cost(center, positions):
    return sum((n := abs(pos - center)) * (n + 1) // 2 for pos in positions)


def least_triangular_cost(positions: list[int]):
    # The triangular cost is the combination of distance and distance squared
    # The arithmetic mean minimises the distance squared, so it is a good starting point
    mean = sum(positions) / len(positions)
    upper_guess, lower_guess = math.ceil(mean), math.floor(mean)
    upper_cost, lower_cost = (
        triangular_cost(guess, positions) for guess in (upper_guess, lower_guess)
    )
    # search starting at the best guess
    # The cost is strictly ascending/descending; check if we need to search up or down
    if upper_cost < lower_cost:
        direction, best_cost, best_guess = 1, upper_cost, upper_guess
    else:
        direction, best_cost, best_guess = -1, lower_cost, lower_guess
    while True:
        next_guess = best_guess + direction
        next_cost = triangular_cost(next_guess, positions)
        if next_cost > best_cost:
            return best_cost
