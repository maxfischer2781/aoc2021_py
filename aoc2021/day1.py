def solve(in_stream):
    data = list(map(int, in_stream))
    return increases(data), window_increases(data)


def increases(report: list[int]):
    """The number of times the next report is larger than the previous one"""
    return sum(prev < curr for prev, curr in zip(report[:-1], report[1:]))


def window_increases(report: list[int]):
    """The number of times the next report window is larger than the previous one"""
    # Two adjacent windows A, B, C and B, C, D share the middle elements B, C
    # The only relevant difference for the sum is A < D
    return sum(prev < curr for prev, curr in zip(report[:-1], report[3:]))
