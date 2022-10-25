# Goal: Given a sequence of Bingo numbers, find the winner/loser.
# This is a straightforward "interpret the instructions" approach.
from typing import Iterator
from copy import deepcopy


class BingoBoard:
    """
    Representation of a bingo board

    This type is optimised for marking of drawn numbers and checking if done.
    For the former, we keep a `set` of numbers on the board; this allows to
    quickly check if anything needs to be marked.
    For the latter, we keep *all* rows and columns; this allows to quickly check
    if a row or columns is done.
    """
    def __init__(self, board: list[list[int]]):
        #: the combinations needed to win, i.e. horizontal/vertical groups
        self.combinations: list[set[int]] = [set(row) for row in board] + [
            set(column) for column in zip(*board)
        ]
        #: all the numbers in this board
        self.numbers = {num for row in board for num in row}
        assert len(self.numbers) == sum(map(len, board))

    def draw(self, number: int):
        """Mark the current drawn `number` on the board, return whether we hit Bingo"""
        # check whether we remove anything at all before going through all combinations
        if number in self.numbers:
            self.numbers.discard(number)
            for combination in self.combinations:
                combination.discard(number)
                if not combination:
                    return True
        return False


def read_input(data: Iterator[str]):
    """Parse the input into drawn numbers and :py:class:`~.BingoBoard` s"""
    # the first line (`next(data)`) is a comma-separate (`.split(",")`) integer list
    numbers = list(map(int, next(data).strip().split(",")))
    yield numbers
    if next(data) != "\n":
        raise ValueError("expected empty line after header")
    buffer = []
    for line in data:
        if line == "\n":
            yield BingoBoard(buffer)
            buffer = []
        else:
            buffer.append(list(map(int, line.split())))
    if buffer:
        yield BingoBoard(buffer)


def solve(in_stream):
    numbers, *boards = read_input(iter(in_stream))
    winner, win_draw = find_winner(numbers, deepcopy(boards))
    loser, lose_draw = find_loser(numbers, deepcopy(boards))
    return sum(winner.numbers) * win_draw, sum(loser.numbers) * lose_draw


def find_winner(numbers: list[int], boards: list[BingoBoard]):
    """Find the first board to win given the drawn `numbers`"""
    for number in numbers:
        for board in boards:
            if board.draw(number):
                return board, number


def find_loser(numbers: list[int], boards: list[BingoBoard]):
    """Find the last board to win given the drawn `numbers`"""
    for number in numbers:
        for board in boards[:]:
            if board.draw(number):
                if len(boards) > 1:
                    boards.remove(board)
                else:
                    return board, number
