from io import StringIO


POSITION = tuple[int, int]


def solve(in_stream: StringIO) -> tuple[object, object]:
    down, right, size = parse(in_stream)
    return converge(down=down, right=right, size=size) + 1, "???"


def parse(in_stream: StringIO) -> tuple[set[POSITION], set[POSITION], POSITION]:
    down, right = set(), set()
    for row_idx, row in enumerate(map(str.strip, in_stream)):
        for col_idx, symbol in enumerate(row):
            if symbol == "v":
                down.add((row_idx, col_idx))
            elif symbol == ">":
                right.add((row_idx, col_idx))
    return down, right, (row_idx+1, col_idx+1)


def converge(down: set[POSITION], right: set[POSITION], size: POSITION):
    steps = 0
    while True:
        # east-facing
        diff = []
        for pos in right:
            next_pos = pos[0], (pos[1] + 1) % size[1]
            if next_pos not in right and next_pos not in down:
                diff.append((pos, next_pos))
        done = not diff
        for old_pos, new_pos in diff:
            right.discard(old_pos)
            right.add(new_pos)
        # south-facing
        diff = []
        for pos in down:
            next_pos = (pos[0] + 1) % size[0], pos[1]
            if next_pos not in right and next_pos not in down:
                diff.append((pos, next_pos))
        done = done and not diff
        for old_pos, new_pos in diff:
            down.discard(old_pos)
            down.add(new_pos)
        if not done:
            steps += 1
        else:
            break
    return steps
