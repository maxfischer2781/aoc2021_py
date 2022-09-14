import operator


def solve(in_stream):
    data = list(in_stream)
    return operator.mul(*follow(data)), operator.mul(*navigate(data))


def follow(commands: list[str]):
    """Interpret commands directly"""
    horizontal, depth = 0, 0
    for command in commands:
        direction, value = command.split()
        if direction == "forward":
            horizontal += int(value)
        elif direction == "down":
            depth += int(value)
        elif direction == "up":
            depth -= int(value)
    return horizontal, depth


def navigate(commands: list[str]):
    """Interpret commands as move+aim"""
    horizontal, depth, aim = 0, 0, 0
    for command in commands:
        direction, value = command.split()
        if direction == "forward":
            horizontal += int(value)
            depth += aim * int(value)
        elif direction == "down":
            aim += int(value)
        elif direction == "up":
            aim -= int(value)
    return horizontal, depth
