from collections import Counter
from io import StringIO


def solve(in_stream: StringIO):
    start_population = list(map(int, in_stream.read().split(",")))
    return simulate(start_population, 80), simulate(start_population, 256)


# This is a straightforward translation of the task description
# The only but very major optimisation is that instead of tracking each fish with
# separate hatching time, we only track the number of fish per hatching time. This
# means we stay at a constant sized list of length 9 (from 0 upt to 8 days) no matter
# the population. As a result, each day has exactly the same cost to calculate.
def simulate(start_population: list[int], days: int):
    """Simulate the population expanding over several `days`"""
    # A mapping of "remaining days" => "population count"
    timed_population = Counter(start_population)
    for _day in range(days):
        # for every "0 remaining days" fish we hatch a new one
        hatching = timed_population[0]
        # decrease remaining days
        for new_index in range(8):
            timed_population[new_index] = timed_population[new_index + 1]
        timed_population[6] += hatching  # reset time for fish that just bred
        timed_population[8] = hatching  # long timer for newly bred fish
    return sum(timed_population.values())


# Possible improvements:
# - since days cover the range 0-8, use a list of length 9 instead of the Counter
# - instead of moving counts between remaining days, we could
#   - keep the days constant and cycle through them modulo 7
#   - keep and extra store for newly hatched, since they are larger than the cycle
