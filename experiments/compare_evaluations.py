"""Reproduces the evaluation-design evidence quoted in Question1_Group.ipynb.

Each row plays the final design against one altered design, both searching to depth 3.
Every game starts from a random 4-ply opening, and each opening is played twice with the
sides swapped, so neither design gains from the start position.
Score = (wins + draws / 2) / games, from the final design's side.

Usage: python3 compare_evaluations.py [openings]     default 500 openings = 1000 games per row
"""
import multiprocessing
import random
import sys

ROWS, COLUMNS = 6, 7
EMPTY, FIRST, SECOND = 0, 1, 2
CENTRE = 3
WIN_SCORE = 1000000
CENTRE_FIRST = [3, 2, 4, 1, 5, 0, 6]
DEPTH = 3


def build_lines():
    lines = []
    for row in range(ROWS):
        for column in range(COLUMNS):
            for row_step, column_step in ((0, 1), (1, 0), (1, 1), (-1, 1)):
                cells = [(row + i * row_step, column + i * column_step) for i in range(4)]
                if all(0 <= r < ROWS and 0 <= c < COLUMNS for r, c in cells):
                    lines.append(cells)
    return lines


LINES = build_lines()


def moves(board):
    return [column for column in CENTRE_FIRST if board[0][column] == EMPTY]


def drop(board, column, player):
    for row in range(ROWS - 1, -1, -1):
        if board[row][column] == EMPTY:
            board[row][column] = player
            return row
    raise ValueError(column)


def has_won(board, player):
    return any(all(board[r][c] == player for r, c in line) for line in LINES)


def playable(board, row, column):
    return row == ROWS - 1 or board[row + 1][column] != EMPTY


def design(line_values, opponent_threat=0, own_threat=0, centre=0):
    return {"values": line_values, "opponent_threat": opponent_threat,
            "own_threat": own_threat, "centre": centre}


FINAL = design((1, 3, 9), opponent_threat=100)
ALTERED = [
    ("No evaluation (every leaf scores 0)", design((0, 0, 0))),
    ("No next-move threat penalty", design((1, 3, 9))),
    ("Same style of bonus for the computer's own threes (+30)", design((1, 3, 9), 100, 30)),
    ("No single-disc lines (0/3/9)", design((0, 3, 9), 100)),
    ("Steeper top end (1/3/27)", design((1, 3, 27), 100)),
    ("Flatter scale (1/2/4)", design((1, 2, 4), 100)),
    ("Steeper scale (1/4/16)", design((1, 4, 16), 100)),
    ("Extra centre-column bonus (+2 per disc)", design((1, 3, 9), 100, 0, 2)),
    ("Threat penalty 1,000 instead of 100", design((1, 3, 9), 1000)),
]


def line_score(board, me, values):
    them = FIRST if me == SECOND else SECOND
    score = 0
    for line in LINES:
        cells = [board[r][c] for r, c in line]
        mine, theirs = cells.count(me), cells.count(them)
        if mine and not theirs:
            score += values[mine - 1]
        elif theirs and not mine:
            score -= values[theirs - 1]
    return score


def evaluate(board, me, spec):
    them = FIRST if me == SECOND else SECOND
    score = line_score(board, me, spec["values"])
    for line in LINES:
        cells = [board[r][c] for r, c in line]
        if EMPTY not in cells:
            continue
        r, c = line[cells.index(EMPTY)]
        if cells.count(them) == 3 and playable(board, r, c):
            score -= spec["opponent_threat"]
        elif cells.count(me) == 3 and playable(board, r, c):
            score += spec["own_threat"]
    if spec["centre"]:
        for row in range(ROWS):
            if board[row][CENTRE] == me:
                score += spec["centre"]
            elif board[row][CENTRE] == them:
                score -= spec["centre"]
    return score


def minimax(board, depth, my_turn, me, spec):
    them = FIRST if me == SECOND else SECOND
    if has_won(board, me):
        return WIN_SCORE + depth
    if has_won(board, them):
        return -(WIN_SCORE + depth)
    columns = moves(board)
    if not columns:
        return 0
    if depth == 0:
        return evaluate(board, me, spec)
    values = []
    for column in columns:
        row = drop(board, column, me if my_turn else them)
        values.append(minimax(board, depth - 1, not my_turn, me, spec))
        board[row][column] = EMPTY
    return max(values) if my_turn else min(values)


def choose(board, me, spec):
    best_value, best_column = None, None
    for column in moves(board):
        row = drop(board, column, me)
        value = minimax(board, DEPTH - 1, False, me, spec)
        board[row][column] = EMPTY
        if best_value is None or value > best_value:
            best_value, best_column = value, column
    return best_column


def play_one(job):
    """Return +1 if the final design wins, -1 if it loses, 0 for a draw."""
    other_spec, seed, final_starts = job
    rng = random.Random(seed)
    board = [[EMPTY] * COLUMNS for _ in range(ROWS)]
    final_side = FIRST if final_starts else SECOND
    player = FIRST
    for _ in range(4):
        drop(board, rng.choice(moves(board)), player)
        player = FIRST if player == SECOND else SECOND
    while True:
        spec = FINAL if player == final_side else other_spec
        drop(board, choose(board, player, spec), player)
        if has_won(board, player):
            return 1 if player == final_side else -1
        if not moves(board):
            return 0
        player = FIRST if player == SECOND else SECOND


def ordinary_score_range(games=150):
    """How large do plain line totals get at the positions the search really evaluates?"""
    plain = []

    def walk(board, depth, my_turn, me):
        them = FIRST if me == SECOND else SECOND
        if has_won(board, FIRST) or has_won(board, SECOND) or not moves(board):
            return
        if depth == 0:
            plain.append(abs(line_score(board, me, FINAL["values"])))
            return
        for column in moves(board):
            row = drop(board, column, me if my_turn else them)
            walk(board, depth - 1, not my_turn, me)
            board[row][column] = EMPTY

    for seed in range(games):
        rng = random.Random(seed)
        board = [[EMPTY] * COLUMNS for _ in range(ROWS)]
        player = FIRST
        for _ in range(4):
            drop(board, rng.choice(moves(board)), player)
            player = FIRST if player == SECOND else SECOND
        while True:
            walk(board, DEPTH, True, player)
            column = choose(board, player, FINAL) if rng.random() < 0.7 else rng.choice(moves(board))
            drop(board, column, player)
            if has_won(board, player) or not moves(board):
                break
            player = FIRST if player == SECOND else SECOND
    return len(plain), max(plain)


def main():
    openings = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    print("Final design: line values 1/3/9, next-move threat penalty 100, depth 3")
    print("{} games per row\n".format(openings * 2))
    with multiprocessing.Pool() as pool:
        for name, spec in ALTERED:
            jobs = [(spec, seed, side) for seed in range(openings) for side in (True, False)]
            results = pool.map(play_one, jobs, chunksize=4)
            wins, draws, losses = results.count(1), results.count(0), results.count(-1)
            score = 100 * (wins + draws / 2) / len(results)
            print("{:<58} W {:>4}  D {:>3}  L {:>4}  score {:5.1f}%".format(name, wins, draws, losses, score), flush=True)
    leaves, largest = ordinary_score_range()
    print("\nLargest plain line total seen: {} across {} evaluated positions".format(largest, leaves))


if __name__ == "__main__":
    main()
