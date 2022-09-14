from io import StringIO


def solve(in_stream: StringIO):
    patterns = [
        (signal.split(), output.split())
        for signal, output in (line.split("|") for line in in_stream)
    ]
    return unique_output(patterns), sum(output_values(patterns))


def unique_output(patterns):
    """Check how many outputs correspond to unique patterns"""
    # unique numbers have 2, 4, 3, or 7 elements – we do not care which they are exactly
    # sum'ing booleans is equivalent to counting 1 for each True value
    return sum(
        length in (2, 4, 3, 7) for _, output in patterns for length in map(len, output)
    )


# Map from display panel combinations to their respective values
# We use frozensets as keys so that we do not have to care about
# the order of panels in a combination. Unlike normal sets, frozensets
# are immutable and thus hashable.
segments = {
    frozenset("abcefg"): 0,
    frozenset("cf"): 1,
    frozenset("acdeg"): 2,
    frozenset("acdfg"): 3,
    frozenset("bcdf"): 4,
    frozenset("abdfg"): 5,
    frozenset("abdefg"): 6,
    frozenset("acf"): 7,
    frozenset("abcdefg"): 8,
    frozenset("abcdfg"): 9,
}


def output_values(patterns):
    """Reconstruct the sum of outputs per pattern"""
    for signal, output in patterns:
        segment_map = solve_mapping(signal)
        # our solver provides real -> display mapping, but we need the reverse
        segment_translation = str.maketrans(
            {value: key for key, value in segment_map.items()}
        )
        total = 0
        # We enumerate in reverse to know the place of each digit i.e. the power of ten
        for i, digit in enumerate(reversed(output)):
            value = segments[frozenset(digit.translate(segment_translation))]
            total += value * (10 ** i)
        yield total


def solve_mapping(signal: "list[str]") -> "dict[str, int]":
    """Reconstruct the real -> display panel mapping"""
    # There is no deeper wisdom to this: It is the result of manually solving the panel
    # overlap and number identification.
    #
    # The s_XY and dXY variables are sets of display panels corresponding to a specific
    # set of real panels or numbers (which are also sets of all their panels). This lets
    # us "subtract" the set of panels/numbers.
    # For example, number 1 (`d1`) and 7 (`d7`) are the panels {"c", "f"} and
    # {"a", "c", "f"} – their set difference (`d7 - d1`) is just the panel {"a"}.
    #
    # When an operation is guaranteed to give one result, we use unpacking assignment
    # to get the one result – for example, `panel_a, = {"a"}` (note the comma) would
    # assign `"a`" to `panel_a` by unpacking the set.
    segment_map = {}
    by_length = sorted(map(set, signal), key=len)
    # uniquely identifiable numbers
    d1 = by_length[0]
    d7 = by_length[1]
    d4 = by_length[2]
    d8 = by_length[-1]
    d235 = by_length[3:6]
    d069 = by_length[6:9]
    # 7:acf - 1:cf
    s_a = (segment_map["a"],) = d7 - d1
    s_bd = d4 - d1
    s_eg = d8 - d4 - d7
    (d0,) = (digit for digit in d069 if not s_bd < digit)
    s_d = (segment_map["d"],) = d8 - d0
    s_b = (segment_map["b"],) = s_bd - s_d
    (d9,) = (digit for digit in d069 if not s_eg < digit)
    (d6,) = (digit for digit in d069 if digit != d0 and digit != d9)
    s_e = (segment_map["e"],) = d8 - d9
    s_g = (segment_map["g"],) = s_eg - s_e
    s_c = (segment_map["c"],) = d8 - d6
    s_f = (segment_map["f"],) = d1 - s_c
    return segment_map
