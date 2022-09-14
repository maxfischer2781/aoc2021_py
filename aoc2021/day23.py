from typing import TypeVar, Hashable, Callable, Iterator
from io import StringIO
from collections import defaultdict
import heapq
import sys

H = TypeVar("H", bound=Hashable)


class Heap(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        heapq.heapify(self)

    def push(self, item):
        return heapq.heappush(self, item)

    def pop(self, index=None):
        if index is None:
            return heapq.heappop(self)
        return super().pop(index)


def solve(in_stream: StringIO) -> tuple[object, object]:
    board = list(in_stream)
    initial = parse(iter(board))
    expected = tuple(
        frozenset({(home, 1), (home, 2)})
        for home in AMPHIPOD_HOMES.values()
    )
    minimum_cost = a_star(
        initial,
        expected,
        neighbours=moves,
        distance=move_cost,
        heuristic=finish_guess,
    )
    expanded_initial = parse_expanded(iter(board))
    expanded_expected = tuple(
        frozenset({(home, 1), (home, 2), (home, 3), (home, 4)})
        for home in AMPHIPOD_HOMES.values()
    )
    minimum_cost_expanded = a_star(
        expanded_initial,
        expanded_expected,
        neighbours=moves,
        distance=move_cost,
        heuristic=finish_guess,
    )
    return minimum_cost, minimum_cost_expanded


HALLWAY_LENGTH = 11
AMPHIPOD_NAMES = {pod_id: name for pod_id, name in enumerate("ABCD")}
AMPHIPOD_IDS = {name: pod_id for pod_id, name in AMPHIPOD_NAMES.items()}
AMPHIPOD_HOMES = {pod_id: 2 * (pod_id + 1) for pod_id in AMPHIPOD_NAMES.keys()}
AMPHIPOD_COSTS = {pod_id: 10 ** pod_id for pod_id in AMPHIPOD_NAMES.keys()}
ROOM_ENTRIES = frozenset(AMPHIPOD_HOMES.values())


# left-right, up-down
# (0, 0) is the leftmost hall position
# (4, 2) is the bottom Bronze home
POSITION = tuple[int, int]
STATE = tuple[frozenset[POSITION], ...]


def parse(in_stream: Iterator[str]) -> STATE:
    # #############
    # #...........#
    # ###A#C#B#C###
    #   #D#A#D#B#
    #   #########
    next(in_stream)
    positions = {pod_id: [] for pod_id in AMPHIPOD_NAMES}
    for down, line in enumerate(in_stream):
        for right, char in enumerate(line[1:]):
            if char in AMPHIPOD_IDS:
                positions[AMPHIPOD_IDS[char]].append((right, down))
    return tuple(frozenset(pods) for _, pods in sorted(positions.items()))


def parse_expanded(in_stream: Iterator[str]) -> STATE:
    # #############
    # #...........#
    # ###A#C#B#C###
    #>  #D#C#B#A#
    #>  #D#B#A#C#
    #   #D#A#D#B#
    #   #########
    def stitch_stream(stream: Iterator[str]):
        next(in_stream)        # discard leading ###
        yield next(in_stream)  # #...
        yield next(in_stream)  # ###A
        yield "  #D#C#B#A#"
        yield "  #D#B#A#C#"
        yield from in_stream

    positions = {pod_id: [] for pod_id in AMPHIPOD_NAMES}
    for down, line in enumerate(stitch_stream(in_stream)):
        for right, char in enumerate(line[1:]):
            if char in AMPHIPOD_IDS:
                positions[AMPHIPOD_IDS[char]].append((right, down))
    return tuple(frozenset(pods) for _, pods in sorted(positions.items()))


def unparse_state(state: STATE) -> str:
    result_lines = []
    positions = {
        pod: AMPHIPOD_NAMES[pod_id]
        for pod_id, pods in enumerate(state)
        for pod in pods
    }
    template = """\
#############
#...........#
###.#.#.#.###
  #.#.#.#.#
  #########""".splitlines()
    for down, line in enumerate(template, start=-1):
        current_line = []
        for right, char in enumerate(line, start=-1):
            current_line.append(positions.get((right, down), char))
        result_lines.append("".join(current_line))
    return "\n".join(result_lines)


def manhattan(a: POSITION, b: POSITION) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def free_path(start: POSITION, stop: POSITION, occupied: set[POSITION]) -> bool:
    current = start
    direction = 1 if stop[0] > start[0] else -1, 1 if stop[1] > start[1] else -1
    if direction[1] > 0:
        while current[0] != stop[0]:
            current = current[0] + direction[0], current[1]
            if current in occupied:
                return False
        while current[1] != stop[1]:
            current = current[0], current[1] + direction[1]
            if current in occupied:
                return False
    else:
        while current[1] != stop[1]:
            current = current[0], current[1] + direction[1]
            if current in occupied:
                return False
        while current[0] != stop[0]:
            current = current[0] + direction[0], current[1]
            if current in occupied:
                return False
    return True


def replace(pod_id, old_pos, new_pos, state: STATE) -> STATE:
    return tuple(
        opods if opod_id != pod_id else frozenset(
            new_pos if spod == old_pos else spod for spod in opods
        )
        for opod_id, opods in enumerate(state)
    )


def moves(current: STATE) -> list[STATE]:
    next_states = []
    occupied = {pos for pods in current for pos in pods}
    for pod_id, pods in enumerate(current):
        # all pods are home, group is done
        if pods == {(AMPHIPOD_HOMES[pod_id], i+1) for i in range(len(pods))}:
            continue
        for pod in pods:
            # pod is at home and not blocking anyone, it no longer needs to move
            if (
                pod[0] == AMPHIPOD_HOMES[pod_id]
                and {
                    (AMPHIPOD_HOMES[pod_id], o) for o in range(len(pods), 1, -1)
                } <= pods
            ):
                continue
            # pod is in the hall, it can only move home
            if pod[1] == 0:
                if all(
                    opod[0] != AMPHIPOD_HOMES[pod_id]
                    for opod_id, opods in enumerate(current)
                    for opod in opods
                    if opod_id != pod_id
                ):
                    target = (AMPHIPOD_HOMES[pod_id], 1)
                    if not free_path(pod, target, occupied):
                        continue
                    for home_pos in range(2, len(pods)+1):
                        next_target = (AMPHIPOD_HOMES[pod_id], home_pos)
                        if not free_path(pod, next_target, occupied):
                            break
                        target = next_target
                    next_states.append(replace(pod_id, pod, target, current))
            # pod is in a home, it can only move to the hall
            elif free_path(pod, (pod[0], 0), occupied):
                for hall_pos in range(HALLWAY_LENGTH):
                    if hall_pos in ROOM_ENTRIES:
                        continue
                    target = (hall_pos, 0)
                    if not free_path(pod, target, occupied):
                        continue
                    next_states.append(replace(pod_id, pod, target, current))
    return next_states


def move_cost(old: STATE, new: STATE) -> int:
    total = 0
    for pod_id, (old_pods, new_pods) in enumerate(zip(old, new)):
        if old_pods == new_pods:
            continue
        movement = old_pods ^ new_pods
        total += AMPHIPOD_COSTS[pod_id] * manhattan(*movement)
    return total


def finish_guess(current: STATE, target: STATE) -> int:
    total = 0
    for pod_id, pods in enumerate(current):
        for pod in pods:
            total += AMPHIPOD_COSTS[pod_id] * abs(pod[0] - AMPHIPOD_HOMES[pod_id])
    return total


def path(target, parents):
    result = [target]
    while True:
        try:
            target = parents[target]
        except KeyError:
            return result
        else:
            result.append(target)


def a_star(
    start: H,
    target: H,
    neighbours: Callable[[H], list[H]],
    distance: Callable[[H, H], int],
    heuristic: Callable[[H, H], int],
) -> tuple[H, int]:
    costs: dict[H, int] = defaultdict(lambda: sys.maxsize, {start: 0})
    visited: set[H] = set()
    # store heuristic-cost, cost and node
    to_visit = Heap([(0, 0, start)])
    while to_visit:
        _, cost, current = to_visit.pop()
        visited.add(current)
        if current == target:
            return cost
        for neighbour in neighbours(current):
            if neighbour in visited:
                pass
            new_cost = cost + distance(current, neighbour)
            if new_cost < costs[neighbour]:
                costs[neighbour] = new_cost
                to_visit.push(
                    (new_cost + heuristic(neighbour, target), new_cost, neighbour)
                )
    raise ValueError("No path to target")
