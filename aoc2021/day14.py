from typing import Iterable
from io import StringIO
from collections import Counter


RULES = dict[tuple[str, str], str]


def read_instructions(in_stream: StringIO) -> tuple[str, RULES]:
    template = next(in_stream).strip()
    next(in_stream)
    return template, {
        tuple(pair.strip()): insertion.strip()
        for pair, insertion in (rule.split("->") for rule in in_stream)
    }


def solve(in_stream: StringIO) -> tuple[object, object]:
    template, rules = read_instructions(in_stream)
    counts = expand_count(template, 10, rules, {}).most_common()
    counts_40 = expand_count(template, 40, rules, {}).most_common()
    return counts[0][1] - counts[-1][1], counts_40[0][1] - counts_40[-1][1]


def expand_count(template: str, steps: int, rules: RULES, memo) -> Counter:
    result = Counter(template[0])
    for pair in pairwise(template):
        key = *pair, steps
        try:
            expanded = memo[key]
        except KeyError:
            if steps == 1:
                expanded = memo[key] = Counter((rules[pair], *pair))
            else:
                expanded = memo[key] = expand_count(pair[0] + rules[pair] + pair[-1], steps - 1, rules, memo)
        result[pair[0]] -= 1
        result += expanded
    return result


def pairwise(itr: Iterable[str]) -> Iterable[tuple[str, str]]:
    iterator = iter(itr)
    prev = next(iterator)
    for current in iterator:
        yield prev, current
        prev = current
