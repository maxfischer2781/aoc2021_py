from io import StringIO


def solve(in_stream: StringIO) -> tuple[object, object]:
    board = [[int(field) for field in line.strip()] for line in in_stream]
    # both functions modify the board – we rely on the synchronization happening
    # after the first 100 steps
    return simulate_totals(board, 100), 100 + simulate_synchronizing(board)


def neighbours(row: int, column: int, grid: list[list[int]]):
    """Yield the up, down, left, right positions of (row, column)"""
    if row == 0:
        rows = (0, 1)
    elif row == len(grid) - 1:
        rows = (row - 1, row)
    else:
        rows = (row - 1, row, row + 1)
    if column == 0:
        columns = (0, 1)
    elif column == len(grid[0]) - 1:
        columns = (column - 1, column)
    else:
        columns = (column - 1, column, column + 1)
    return [(r, c) for r in rows for c in columns if r != row or c != column]


# Both part 1 and 2 need an "advance one step" primitive
def simulate_flashes(board: list[list[int]]):
    """Simulate the next step and return the total number of flashes"""
    flashing, flashed = set(), set()
    for row, row_values in enumerate(board):
        for column, value in enumerate(row_values):
            if value == 9:
                flashing.add((row, column))
            else:
                board[row][column] += 1
    while flashing:
        row, column = flashing.pop()
        flashed.add((row, column))
        board[row][column] = 0
        for row, column in neighbours(row, column, board):
            if (row, column) in flashed:
                continue
            if board[row][column] == 9:
                flashing.add((row, column))
            else:
                board[row][column] += 1
    return len(flashed)


def simulate_totals(board: list[list[int]], steps: int):
    """Simulate `steps` of flashing and return the flash count"""
    total_flashes = 0
    for _ in range(steps):
        total_flashes += simulate_flashes(board)
    return total_flashes


def simulate_synchronizing(board: list[list[int]]):
    """Simulate until the entire board flashes"""
    steps = 1
    board_size = sum(map(len, board))
    while simulate_flashes(board) < board_size:
        steps += 1
    return steps
