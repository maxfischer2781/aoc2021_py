from typing import Protocol, Any, Optional
import argparse
import time
import pathlib
import io
import importlib


class Solution(Protocol):
    def solve(self, data: io.StringIO) -> tuple[Any, Any]:
        raise NotImplementedError

    @property
    def FORMAT(self) -> str:
        raise NotImplementedError


def load_solution(day: int) -> Optional[Solution]:
    """Load the solution for a given day"""
    try:
        module = importlib.import_module(f".day{day}", __package__)
    except ImportError:
        return None
    else:
        if not hasattr(module, "FORMAT"):
            module.FORMAT = "Part 1: {}\nPart 2: {}"
        return module


SOLUTIONS = {day: load_solution(day) for day in range(1, 26)}


def format_duration(delta: float):
    """Format a duration in seconds as a 3-digit SI unit duration"""
    for symbol in ("s", "ms", "μs", "ns"):
        if delta > 0.5:
            break
        delta = delta * 1000
    return f"{delta:.2f} {symbol}"


def run_solution(day: int, example: bool, data_dir: pathlib.Path):
    print(f"[> ### Day {day:3d} ### <]")
    solution = load_solution(day)
    if solution is not None:
        input_path = data_dir / (f"day{day}_ex.txt" if example else f"day{day}.txt")
        data = io.StringIO(input_path.read_text())
        solver, template = solution.solve, solution.FORMAT.strip()
        pre = time.time()
        results = solver(data)
        end = time.time()
        print(f"[> Elapsed {format_duration(end-pre)} <]")
        print(template.format(*results))
    else:
        print("No solution yet!")
        print("Stay tuned... 🎁")
    print(f"[> ### Day {day:3d} ### <]")


CLI = argparse.ArgumentParser()
CLI.add_argument(
    "DAY",
    default=[max(SOLUTIONS, key=lambda x: (SOLUTIONS[x] is not None, x))],
    nargs="*",
    type=int,
)
CLI.add_argument("-e", "--example", action="store_true", help="use example data")
CLI.add_argument(
    "--data",
    type=pathlib.Path,
    default=pathlib.Path.cwd() / "data",
    help="path to directory with daily input",
)

opts = CLI.parse_args()
for d in opts.DAY:
    assert d in SOLUTIONS, f"days {', '.join(map(str, SOLUTIONS))} available, not {d}"
    run_solution(d, opts.example, opts.data)
