from io import StringIO
from collections import defaultdict
from itertools import cycle, product


def parse(in_stream: StringIO) -> tuple[int, int]:
    # Player 1 starting position: 8
    # Player 2 starting position: 10
    return int(next(in_stream).split()[-1]), int(next(in_stream).split()[-1])


def solve(in_stream: StringIO) -> tuple[object, object]:
    players = parse(in_stream)
    second, throws = play_deterministic(*players, target=1000)
    player_moves = [winning_moves(player, target=21) for player in players]
    return second * throws, dirac_winner(*player_moves)


def play_deterministic(*players: int, target: int) -> tuple[int, int]:
    scores = [0] * len(players)
    positions = list(players)
    dice = cycle(range(0, 10))  # infinite dice % 10
    next(dice)  # start at 1
    throws = 0
    while True:
        for player in [0, 1]:
            throws += 3
            positions[player] += next(dice) + next(dice) + next(dice)
            positions[player] = (positions[player] - 1) % 10 + 1
            scores[player] += positions[player]
            if scores[player] >= target:
                return scores[(player + 1) % 2], throws


# part 2


# position -> score -> #universes
GAME_UNIVERSES = dict[int, dict[int, int]]
# dice total -> count
Q_THROW = dict[int, int]
# ({win_moves: universes, ...}, {active_moves: universes})
DIRAC_MOVES = tuple[dict[int, int], dict[int, int]]


def dirac_counts(sides: int, throws: int) -> Q_THROW:
    """How often each result occurs"""
    result_counts = defaultdict(int)
    for dices in product(range(1, sides+1), repeat=throws):
        result_counts[sum(dices)] += 1
    return dict(result_counts)


def winning_moves(position: int, target: int) -> tuple[dict[int, int], dict[int, int]]:
    """Calculate the universes per moves active and reaching the target"""
    throws = dirac_counts(3, 3)
    # position -> score -> universes
    universes: GAME_UNIVERSES = {position: {0: 1}}
    completed_games = {}
    active_games = {}
    moves = 0
    while universes:
        moves += 1
        universes, completed = move(universes, throws, target)
        if completed:
            completed_games[moves] = completed
        active_games[moves] = sum(
            sum(multi_scores.values()) for multi_scores in universes.values()
        )
    return completed_games, active_games


def move(
    universes: GAME_UNIVERSES, throws: Q_THROW, target: int
) -> tuple[GAME_UNIVERSES, int]:
    """Make one move, returning the new universes and completed games"""
    new_universe: GAME_UNIVERSES = defaultdict(lambda: defaultdict(int))
    completed = 0
    for position, scores in universes.items():
        for throw, count in throws.items():
            new_position = (position + throw - 1) % 10 + 1
            for score, score_count in scores.items():
                new_score = score + new_position
                new_count = score_count * count
                if new_score >= target:
                    completed += new_count
                else:
                    new_universe[new_position][new_score] += new_count
    return {
        position: dict(scores) for position, scores in new_universe.items() if scores
    }, completed


def dirac_winner(pl1_moves: DIRAC_MOVES, pl2_moves: DIRAC_MOVES) -> int:
    pl1_wins, pl1_active = pl1_moves
    pl2_wins, pl2_active = pl2_moves
    player1_wins = sum(
        pl1_count * pl2_active[pl1_move-1]
        for pl1_move, pl1_count in pl1_wins.items()
    )
    player2_wins = sum(
        pl2_count * pl1_active[pl2_move]
        for pl2_move, pl2_count in pl2_wins.items()
    )
    return max(player1_wins, player2_wins)
