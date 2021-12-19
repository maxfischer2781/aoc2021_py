from io import StringIO
from collections import Counter
import ast


COORD = tuple[int, ...]


def manhattan(a: COORD, b: COORD) -> int:
    return sum(abs(ai - bi) for ai, bi in zip(a, b))


def pair_key(a: COORD, b: COORD) -> int:
    """Identifier for pairs of coordinates without position, permutation, orientation"""
    # Distance between a and b, squared
    return sum(abs(ai - bi)**2 for ai, bi in zip(a, b))


def shift(a: COORD, b: COORD) -> COORD:
    return tuple(ai - bi for ai, bi in zip(a, b))


def permute(a: COORD, by: tuple[int, ...]) -> COORD:
    # (0, 2, 1) -> flip index 1->2 and 2->1
    return tuple(a[i] for i in by)


def orient(a: COORD, by: tuple[int, ...]) -> COORD:
    return tuple(sign * value for value, sign in zip(a, by))


class Scanner:
    def __init__(self, ident: int, *beacons: COORD, offset: COORD = None):
        self.ident = ident
        self.beacons = beacons
        self.offset = tuple(0 for _ in beacons[0]) if offset is None else offset
        self.profile, self.distances = self._distances(beacons)

    def reorient(self, permutation, orientation, offset: COORD):
        beacons = [
            tuple(
                b - o for b, o in
                zip(orient(permute(beacon, permutation), orientation), offset)
            )
            for beacon in self.beacons
        ]
        beacons.sort()
        clone = type(self)(self.ident, *beacons, offset=offset)
        self.__dict__ = clone.__dict__

    @staticmethod
    def _distances(beacons) -> tuple[Counter[int], dict[int, list[tuple[COORD, COORD]]]]:
        profile = Counter()
        distances = {}
        for i in range(len(beacons)):
            for j in range(i+1, len(beacons)):
                distance = pair_key(beacons[i], beacons[j])
                profile[distance] += 1
                distances.setdefault(distance, []).append((beacons[i], beacons[j]))
        return profile, distances

    @classmethod
    def from_input(cls, in_stream: StringIO):
        # "--- scanner 0 ---\n"
        ident = int(next(in_stream).split()[2])
        beacons = []
        # "-694,-542,520\n"
        for line in in_stream:
            if line == "\n":
                break
            beacons.append(ast.literal_eval(line))
        beacons.sort()
        return cls(ident, *beacons)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.ident}, *{self.beacons})"


def parse(in_stream: StringIO) -> list[Scanner]:
    scanners = []
    try:
        while True:
            scanners.append(Scanner.from_input(in_stream))
    except StopIteration:
        pass
    return scanners


def solve(in_stream: StringIO) -> tuple[object, object]:
    scanners = parse(in_stream)
    reorient_all(scanners)
    beacons = {beacon for scanner in scanners for beacon in scanner.beacons}
    max_manhattan = max(
        manhattan(a.offset, b.offset) for a in scanners for b in scanners
    )
    return len(beacons), max_manhattan


def reorient_all(scanners: list[Scanner]):
    overlap = 3 if len(scanners[0].beacons[0]) == 2 else 12
    fixed = {scanners[0]}
    outstanding = set(scanners[1:])
    while outstanding:
        for candidate_scanner in outstanding:
            for fixed_scanner in fixed:
                if sum(
                    (candidate_scanner.profile & fixed_scanner.profile).values()
                ) >= overlap:
                    if reorient(fixed_scanner, candidate_scanner):
                        fixed.add(candidate_scanner)
                        outstanding.remove(candidate_scanner)
                        break
            else:
                continue
            break


def reorient(fixed: Scanner, candidate: Scanner) -> bool:
    overlaps = fixed.distances.keys() & candidate.distances.keys()
    translation = Counter()
    for overlap in overlaps:
        for fixed_beacons in fixed.distances[overlap]:
            for candidate_beacons in candidate.distances[overlap]:
                fixed_shift = shift(*fixed_beacons)
                candidate_shift = shift(*candidate_beacons)
                abs_fixed_shift = tuple(map(abs, fixed_shift))
                abs_candidate_shift = tuple(map(abs, candidate_shift))
                # ignore ambiguous permutations/orientations
                if (
                    set(abs_candidate_shift) != set(abs_fixed_shift)
                    or len(abs_candidate_shift) != len(set(abs_candidate_shift))
                    or 0 in abs_candidate_shift
                ):
                    continue
                permutation = tuple(
                    abs_candidate_shift.index(abs(fs))
                    for fs in abs_fixed_shift
                )
                signs = tuple(
                    cs//fs
                    for cs, fs in zip(permute(candidate_shift, permutation), fixed_shift)
                )
                # normalise two possible orientations to the "positive" one
                # (1, 1, -1)=1 (-1, -1, 1)=-1
                # (1, 1, 1)=3 (-1, -1, -1)=-3
                for orientation in (signs, tuple(-o for o in signs)):
                    for candidate_beacon in candidate_beacons:
                        for fixed_beacon in fixed_beacons:
                            translated = orient(permute(candidate_beacon, permutation), orientation)
                            translation[permutation, orientation, shift(translated, fixed_beacon)] += 1
    [[[permutation, orientation, offset], count]] = translation.most_common(1)
    if count < 6:
        return False
    candidate.reorient(permutation, orientation, offset)
    return True
