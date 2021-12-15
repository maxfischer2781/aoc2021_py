from typing import Iterable
from io import StringIO
import bisect


def solve(in_stream: StringIO) -> tuple[object, object]:
    risk_map = [[int(field) for field in line.strip()] for line in in_stream]
    expanded_map = expand(risk_map, 5)
    return dijkstra(risk_map), dijkstra(expanded_map)


def expand(risk_map: list[list[int]], repeat: int) -> list[list[int]]:
    new_map = []
    for y in range(repeat):
        for line in risk_map:
            new_map.append([])
            for x in range(repeat):
                new_map[-1].extend((field + x + y - 1) % 9 + 1 for field in line)
    return new_map


def manhattan(a, b):
    ax, ay = a
    bx, by = b
    return abs(ax - bx) + abs(ay - by)


def dijkstra(risk_map: list[list[int]]):
    costs = {(0, 0): 0}
    seen = set()
    order = sorted(((cost, node) for node, cost in costs.items()))
    target = len(risk_map) - 1, len(risk_map[0]) - 1
    while costs:
        best_cost, best_node = order.pop(0)
        seen.add(best_node)
        if best_node == target:
            return best_cost
        for nb in neighbours(*best_node, *target):
            if nb in seen:
                continue
            try:
                nb_cost = costs[nb]
            except KeyError:
                nb_cost = float("inf")
            new_cost = best_cost + risk_map[nb[0]][nb[1]]
            if new_cost < nb_cost:
                costs[nb] = new_cost
                try:
                    nb_index = order.index((nb_cost, nb))
                except ValueError:
                    pass
                else:
                    order.pop(nb_index)
                bisect.insort(order, (new_cost, nb))


def neighbours(row: int, column: int, max_row: int, max_column: int) -> Iterable[tuple[int, int]]:
    """Yield the up, down, left, right positions of (row, column)"""
    if row != 0:
        yield row - 1, column
    if row != max_row:
        yield row + 1, column
    if column != 0:
        yield row, column - 1
    if column != max_column:
        yield row, column + 1
