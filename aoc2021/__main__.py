import argparse
import time
import pathlib
import io

from . import day1
from . import day2
from . import day3
from . import day4
from . import day5
from . import day6


class Unsolved:
    def __init__(self, day: int):
        self.day = day

    def solve(self, *args, **kwargs) -> tuple:
        return ()

    @property
    def FORMAT(self):
        return f"No solution for day {self.day}"


SOLUTIONS = dict(enumerate((day1, day2, day3, day4, day5, day6), start=1))


def format_duration(delta: float):
    for symbol in ("s", "ms", "μs", "ns"):
        if delta > 0.5:
            break
        delta = delta * 1000
    return f"{delta:.2f} {symbol}"


def run_solution(day: int, example: bool):
    print(f"[> ### Day {day:3d} ### <]")
    data_file = f'day{day}_ex.txt' if example else f'day{day}.txt'
    input_path = pathlib.Path(__file__).parent.parent / 'data' / data_file
    data = io.StringIO(input_path.read_text())
    solver, template = SOLUTIONS[day].solve, SOLUTIONS[day].FORMAT.strip()
    pre = time.time()
    results = solver(data)
    end = time.time()
    print(f"[> Elapsed {format_duration(end-pre)} <]")
    print(template.format(*results))
    print(f"[> ### Day {day:3d} ### <]")


CLI = argparse.ArgumentParser()
CLI.add_argument(
    'DAY',
    default=[],
    nargs='*',
    type=int,
)
CLI.add_argument(
    "-e",
    "--example",
    action="store_true"
)

opts = CLI.parse_args()
for d in opts.DAY or [max(SOLUTIONS)]:
    assert d in SOLUTIONS, f"days {', '.join(map(str, SOLUTIONS))} available, not {d}"
    run_solution(d, opts.example)
