from io import StringIO
from math import prod


def solve(in_stream: StringIO):
    heightmap = [[int(point) for point in row.strip()] for row in in_stream]
    largest_basins = sorted(basin_scan(heightmap), key=len)[-3:]
    return sum(point + 1 for point in low_points(heightmap)), prod(
        map(len, largest_basins)
    )


def neighbours(row: int, column: int, grid: list[list[int]]):
    """Yield the up, down, left, right positions of (row, column)"""
    if row != 0:
        yield row - 1, column
    if row != len(grid) - 1:
        yield row + 1, column
    if column != 0:
        yield row, column - 1
    if column != len(grid[0]) - 1:
        yield row, column + 1


# This is a brute-force search
# ============================
# Downside is that we visit each point up to five times:
# - once as a candidate as low point
# - up to four times as a neighbour to compare to
# We could in principle optimise this by e.g. skipping neighbours as candidates once
# we find a low point. However, this inefficiency is a small overhead and alternatives
# are not clearly faster – but more effort to code/maintain.
def low_points(heightmap: list[list[int]]):
    """Find the points lower than all their neighbours"""
    for row, columns in enumerate(heightmap):
        for column, value in enumerate(columns):
            if all(
                value < heightmap[r][c] for r, c in neighbours(row, column, heightmap)
            ):
                yield value


# This algorithm is roughly similar to DBScan/DenGraph clustering
# ===============================================================
# By construction, points of basins are internally connected in a basin
# but fully disconnected across basins. This means for every point we
# can recursively collect its connected ("not 9") neighbours.
# It does not matter where we start collecting: Each point will eventually
# neighbour-recurse through the entire basin but no further. By removing points
# as we collect them into clusters, once we have a complete cluster we are
# guaranteed that the left-over points belong to a new cluster.
def basin_scan(heightmap: list[list[int]]):
    """Scan for basins, i.e. connected points separated by height 9"""
    # Set for quick lookup if a specific point may be part of a basin
    # Due to O(1) containment check, arbitrary draw and deletion, this is an
    # efficient way to keep track of points we still have to visit.
    candidates = {
        (row, column)
        for row, columns in enumerate(heightmap)
        for column, value in enumerate(columns)
        if value < 9
    }
    clusters = []
    # iteratively connect individual points to connected clusters
    while candidates:
        # It does not matter at which point we start: every point is part of one basin;
        # let the candidates set arbitrarily select one to start at.
        current_cluster = [candidates.pop()]
        # The same list can be used to store the result as well as nodes from which
        # we still have to search for neighbours. This exploits that it is safe to
        # iterate over a list while appending to it.
        # The cluster content is guaranteed to be unique and finite since we draw it
        # from the finite candidate set.
        for point in current_cluster:
            for nb in neighbours(*point, heightmap):
                if nb in candidates:
                    current_cluster.append(nb)
                    candidates.remove(nb)
        clusters.append(current_cluster)
    return clusters
