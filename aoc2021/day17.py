from typing import NamedTuple
from io import StringIO
import math


class Target(NamedTuple):
    x_min: int
    x_max: int
    y_min: int
    y_max: int

    def __contains__(self, item: tuple[int, int]):
        return self.x_min <= item[0] <= self.x_max and self.y_min <= item[1] <= self.y_max

    @classmethod
    def parse(cls, instruction: str):
        # target area: x=20..30, y=-10..-5
        x_part, y_part = (part.split("=")[-1] for part in instruction.split(","))
        return cls(
            *(bound for part in (x_part, y_part) for bound in map(int, part.split("..")))
        )


def triangular(n: int) -> int:
    return n * (n + 1) // 2


def solve(in_stream: StringIO) -> tuple[object, object]:
    target = Target.parse(in_stream.readline())
    return triangular(max_y(target)), len(valid_velocities(target))


def min_x(target: Target) -> int:
    """The minimum x velocity to hit the target"""
    # The maximum x range is the triangular number of the velocity:
    # For an initial velocity `n`, we move `n + (n - 1) + (n - 2) + ... 1` distance.
    # Thus, since we know the minimum distance to reach the target, we search the
    # n to the triangular number.
    # The triangular number of `n` is `n * (n + 1) // 2`` < `n^2 // 2`. We can use the
    # latter upper bound as a guess and then search down.
    min_bound = math.ceil(math.sqrt(target.x_max * 2))
    for guess in range(min_bound, 0, -1):
        if triangular(guess) >= target.x_min:
            min_bound = guess
        else:
            break
    return min_bound


def max_x(target: Target) -> int:
    """The maximum x velocity to hit the target"""
    # Hit the target in the first step
    return abs(target.x_max)


def min_y(target: Target) -> int:
    """The minimum y velocity to hit the target"""
    # Hit the target in the first step by dropping down
    return target.y_min


def max_y(target: Target) -> int:
    """The maximum y velocity to hit the target"""
    # The maximum y velocity is *upwards*, meaning that we drop back down.
    # Due to y "acceleration" by -1 per step, if we start with +y velocity we reach
    # height of 0 again with -y velocity (deceleration up is the inverse of
    # acceleration down). Thus, the first step of dropping down happens with ``-(y+1)``
    # velocity.
    # To reach the target `|ty|` in the first step, we need a velocity `y+1 = |ty|` or
    # `y = |ty| - 1`.
    return abs(target.y_min) - 1


def valid_velocities(target: Target) -> list[tuple[int, int]]:
    """Provide all velocities that hit the `target`"""
    return [
        (x_vel, y_vel)
        for x_vel in range(min_x(target), max_x(target) + 1)
        for y_vel in range(min_y(target), max_y(target) + 1)
        if hits(x_vel, y_vel, target)
    ]


def hits(x_vel: int, y_vel: int, target: Target) -> bool:
    x, y = 0, 0
    while x <= target.x_max and y >= target.y_min:
        if (x, y) in target:
            return True
        x += x_vel
        y += y_vel
        y_vel -= 1
        x_vel = 0 if x_vel == 0 else x_vel - 1
    return False
