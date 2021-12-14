from typing import Iterable
from io import StringIO
from collections import Counter


RULES = dict[str, str]


def read_instructions(in_stream: StringIO) -> tuple[str, RULES]:
    template = next(in_stream).strip()
    next(in_stream)
    return template, {
        pair[:2]: pair[0] + insertion.strip() + pair[1]
        for pair, insertion in (rule.split("->") for rule in in_stream)
    }


def solve(in_stream: StringIO) -> tuple[object, object]:
    template, rules = read_instructions(in_stream)
    # we could speed up the second expansion by using the memo of the first
    # that is only about 10% extra performance, though
    return expand_quantity(template, 10, rules), expand_quantity(template, 40, rules)


def expand_quantity(template: str, steps: int, rules: RULES) -> int:
    """Compute the quantity of extremes after ``steps`` times expanding ``template``"""
    counts = expand_count(template, steps, rules, {}).most_common()
    return counts[0][1] - counts[-1][1]


def expand_count(template: str, steps: int, rules: RULES, memo) -> Counter:
    result = Counter(template[0])
    for pair in pairwise(template):
        key = *pair, steps
        try:
            expanded = memo[key]
        except KeyError:
            if steps == 1:
                expanded = memo[key] = Counter(rules[pair])
            else:
                expanded = memo[key] = expand_count(rules[pair], steps - 1, rules, memo)
        result[pair[0]] -= 1
        result += expanded
    return result


def pairwise(itr: Iterable[str]) -> Iterable[str]:
    iterator = iter(itr)
    prev = next(iterator)
    for current in iterator:
        yield prev + current
        prev = current
