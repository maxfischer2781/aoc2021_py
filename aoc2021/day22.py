from typing import NamedTuple
from io import StringIO
from math import prod


class Cube(NamedTuple):
    """
    Cube bounded by [min, max) x, y, z coordinates

    The upper coordinate bound is *ex*clusive so that
    we can easily represent an empty cube.
    """
    x: tuple[int, int]
    y: tuple[int, int]
    z: tuple[int, int]

    @property
    def volume(self):
        return prod(high - low for low, high in self)

    def __lt__(self, other: "Cube"):
        """Self is strictly contained in other"""
        return all(sc[0] > oc[0] and sc[1] < oc[1] for sc, oc in zip(self, other))

    def __le__(self, other: "Cube"):
        """Self is contained in or equal to other"""
        return all(sc[0] >= oc[0] and sc[1] <= oc[1] for sc, oc in zip(self, other))

    def intersects(self, other: "Cube") -> bool:
        """Check whether two cubes intersect"""
        return not any(sc[0] >= oc[1] or oc[0] >= sc[1] for sc, oc in zip(self, other))

    def intersection(self, other: "Cube") -> "Cube":
        """The intersection of two cubes, i.e. the volume contained in both"""
        if not self.intersects(other):
            return Cube((0, 0), (0, 0), (0, 0))
        return Cube(
            *((max(sc[0], oc[0]), min(sc[1], oc[1])) for sc, oc in zip(self, other))
        )

    def difference(self, other: "Cube") -> "list[Cube]":
        """The difference to an ``other`` cube"""
        if not other.intersects(self):
            return [self]
        elif self <= other:
            return []
        leftover = []
        cavity = self.intersection(other)
        if self.x[0] < cavity.x[0]:
            leftover.append(Cube((self.x[0], cavity.x[0]), self.y, self.z))
        if self.x[1] > cavity.x[1]:
            leftover.append(Cube((cavity.x[1], self.x[1]), self.y, self.z))
        if self.y[0] < cavity.y[0]:
            leftover.append(Cube(cavity.x, (self.y[0], cavity.y[0]), self.z))
        if self.y[1] > cavity.y[1]:
            leftover.append(Cube(cavity.x, (cavity.y[1], self.y[1]), self.z))
        if self.z[0] < cavity.z[0]:
            leftover.append(Cube(cavity.x, cavity.y, (self.z[0], cavity.z[0])))
        if self.z[1] > cavity.z[1]:
            leftover.append(Cube(cavity.x, cavity.y, (cavity.z[1], self.z[1])))
        return leftover


class Shape(NamedTuple):
    """A 3D shape representing a voxel cloud"""
    bound: Cube
    cavities: tuple[Cube, ...]

    @property
    def volume(self):
        return self.bound.volume - sum(cavity.volume for cavity in self.cavities)

    def __bool__(self):
        return self.volume > 0

    def __sub__(self, other: Cube) -> "Shape":
        if not self.bound.intersects(other):
            return self
        elif self.bound <= other:
            return Shape(Cube((0, 0), (0, 0), (0, 0)), ())
        cavities = [self.bound.intersection(other)]
        for cavity in self.cavities:
            cavities.extend(cavity.difference(other))
        return Shape(self.bound, tuple(cavities))


def parse_range(literal: str) -> tuple[int, int]:
    # "x=-25..26" -> (-25, 26)
    low, high = map(int, literal.split("=")[-1].split(".."))
    return low, high + 1


INSTRUCTIONS = list[tuple[bool, Cube]]


def parse(in_stream: StringIO) -> INSTRUCTIONS:
    return [
        (x.startswith("on"), Cube(parse_range(x), parse_range(y), parse_range(z)))
        for x, y, z in
        (line.split(",") for line in map(str.strip, in_stream) if line)
    ]


def solve(in_stream: StringIO) -> tuple[object, object]:
    instructions = parse(in_stream)
    return reboot_core(instructions), reboot_all(instructions)


def switch_off(area: Cube, volumes: list[Shape]) -> list[Shape]:
    return [new_volume for volume in volumes if (new_volume := volume - area)]


def switch_on(area: Cube, volumes: list[Shape]) -> list[Shape]:
    pruned = switch_off(area, volumes)
    pruned.append(Shape(area, ()))
    return pruned


def reboot_core(instructions: INSTRUCTIONS) -> int:
    volumes = []
    for on, area in instructions:
        if any(coord[0] < -50 or coord[1] > 51 for coord in area):
            continue
        if on:
            volumes = switch_on(area, volumes)
        else:
            volumes = switch_off(area, volumes)
    return sum(volume.volume for volume in volumes)


def reboot_all(instructions: INSTRUCTIONS) -> int:
    volumes = []
    for on, area in instructions:
        if on:
            volumes = switch_on(area, volumes)
        else:
            volumes = switch_off(area, volumes)
    return sum(volume.volume for volume in volumes)

