from io import StringIO
from collections import Counter
import ast


# Solution notice:
# While the description phrases the Scanner orientation in terms of x, y, z rotations,
# there is actually no need to figure out the actual rotations. It is sufficient to
# compute the permutations and mirroring to *transform* a rotated position back.


COORD = tuple[int, ...]


def permute(a: COORD, by: tuple[int, ...]) -> COORD:
    """Apply a permutation to `a`"""
    # (0, 2, 1) -> flip index 1->2 and 2->1
    return tuple(a[i] for i in by)


def orient(a: COORD, by: tuple[int, ...]) -> COORD:
    """Apply a reorientation to `a`"""
    return tuple(sign * value for value, sign in zip(a, by))


def pair_key(a: COORD, b: COORD) -> int:
    """Identifier for pairs of coordinates without position, permutation, orientation"""
    # Distance between a and b, squared
    # Since we do not need the precise distance, keeping the square is faster
    # (saves computing the square root) and an integer (avoiding float precision).
    return sum(abs(ai - bi)**2 for ai, bi in zip(a, b))


def shift(a: COORD, b: COORD) -> COORD:
    """Vector to move from b to a"""
    return tuple(ai - bi for ai, bi in zip(a, b))


class Scanner:
    """A scanner and all its beacon coordinates"""
    def __init__(self, ident: int, *beacons: COORD, offset: COORD = None):
        self.ident = ident
        self.beacons = beacons
        self.offset = tuple(0 for _ in beacons[0]) if offset is None else offset
        # pre-computed identifiers for pairs of beacons
        # These are independent of the rotation and position of the scanner. This allows
        # finding which scanners overlap in their beacons.
        self.profile, self.distances = self._distances(beacons)

    def reorient(self, permutation, orientation, offset: COORD):
        """Reorient the scanner, adjusting the beacon coordinates and offset"""
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
                # compute an ID that is likely to match for the same beacon pairs under
                # any transformation, and unlikely to match for distinct beacons
                pair_id = pair_key(beacons[i], beacons[j])
                profile[pair_id] += 1
                distances.setdefault(pair_id, []).append((beacons[i], beacons[j]))
        return profile, distances

    @classmethod
    def from_input(cls, in_stream: StringIO):
        """Parse a single scanner block from an input stream"""
        # "--- scanner 0 ---\n"
        ident = int(next(in_stream).split()[2])
        beacons = []
        # "-694,-542,520\n"
        for line in in_stream:
            if line == "\n":
                break
            # the beacon positions just happen to be tuple literals – we can eval them
            beacons.append(ast.literal_eval(line))
        beacons.sort()
        return cls(ident, *beacons)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.ident}, *{self.beacons})"


def parse(in_stream: StringIO) -> list[Scanner]:
    """Parse all Scanners from an input stream"""
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


def manhattan(a: COORD, b: COORD) -> int:
    """Manhattan distance between a and b"""
    return sum(abs(ai - bi) for ai, bi in zip(a, b))


def reorient_all(scanners: list[Scanner]):
    """Reorient all scanners in relation to Scanner 0"""
    overlap = 3 if len(scanners[0].beacons[0]) == 2 else 12
    fixed = {scanners[0]}
    outstanding = set(scanners[1:])
    while outstanding:
        for candidate_scanner in outstanding:
            for fixed_scanner in fixed:
                # The profile is a fuzzy measure on how beacons are positioned.
                # Its intersection is an upper bound on how many beacons are identical.
                # TODO: The profile is about *pairs*. Are we too pessimistic and should
                #       check for overlap//2 instead?
                if sum(
                    (candidate_scanner.profile & fixed_scanner.profile).values()
                ) >= overlap:
                    if reorient(fixed_scanner, candidate_scanner):
                        fixed.add(candidate_scanner)
                        outstanding.remove(candidate_scanner)
                        # break-then-break-else-continue ladder to get out of two loops
                        break
            else:
                continue
            break


def reorient(fixed: Scanner, candidate: Scanner) -> bool:
    overlaps = fixed.distances.keys() & candidate.distances.keys()
    # For each *potentially* overlapping pair, we compute *several* possible
    # translations that brings the candidate in line with the fixed reference.
    # Most of this will be noise, but the correct translation will come up for
    # each pair – meaning it is the most common.
    # Counter.most_common can find it efficiently.
    translation = Counter()
    for overlap in overlaps:
        for fixed_beacons in fixed.distances[overlap]:
            for candidate_beacons in candidate.distances[overlap]:
                # We start with the relative shift since it is independent of offset
                # The absolute values are correct (if the pair matches) so we can just
                # check which position a value ended up.
                # E.g. (1, 14, -12) to (12, 14, 1) is the permutation (2, 1, 0)
                fixed_shift = shift(*fixed_beacons)
                candidate_shift = shift(*candidate_beacons)
                abs_fixed_shift = tuple(map(abs, fixed_shift))
                abs_candidate_shift = tuple(map(abs, candidate_shift))
                # ignore ambiguous permutations/orientations
                if (
                    set(abs_candidate_shift) != set(abs_fixed_shift)
                    # TODO: relax these?
                    or len(abs_candidate_shift) != len(set(abs_candidate_shift))
                    or 0 in abs_candidate_shift
                ):
                    continue
                permutation = tuple(
                    abs_candidate_shift.index(abs(fs))
                    for fs in abs_fixed_shift
                )
                # After permutation, the difference in signs hints which axes need
                # to be mirrored.
                signs = tuple(
                    cs//fs
                    for cs, fs in zip(permute(candidate_shift, permutation), fixed_shift)
                )
                # The orientation is *not* unique from the signs. Since
                # `shift(a, b) == -shift(b, a)` we may be off by factor -1 if we took
                # the pair in the wrong order.
                # Just try both.
                for orientation in (signs, tuple(-o for o in signs)):
                    for candidate_beacon in candidate_beacons:
                        for fixed_beacon in fixed_beacons:
                            translated = orient(permute(candidate_beacon, permutation), orientation)
                            translation[permutation, orientation, shift(translated, fixed_beacon)] += 1
    # the most common orientation
    [[[permutation, orientation, offset], count]] = translation.most_common(1)
    # safety measure in case we did not manage to find a reorientation
    if count < 6:
        return False
    candidate.reorient(permutation, orientation, offset)
    return True
