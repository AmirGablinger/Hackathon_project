import random

def spin_row():
    symbols = ["🍓", "🍍", "🍒", "🍉", "🍇"]
    return [random.choice(symbols) for _ in range(3)]

def get_payout(row, bet):
    if row[0] == row[1] == row[2]:
        if row[0] == '🍒':
            return bet * 15
        elif row[0] in ('🍓', '🍍'):
            return bet * 10
        elif row[0] in ('🍇', '🍉'):
            return bet * 5
    return 0
