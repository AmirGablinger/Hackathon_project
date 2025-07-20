import random
from Blackjack import BlackjackGame
from db import conn
from werkzeug.security import generate_password_hash, check_password_hash
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template, request, session
import psycopg2.extras
from slot_machine import spin_row, get_payout

env_path = Path(__file__).parent / ".env"
print("Looking for .env at:", env_path.resolve())
load_result = load_dotenv(dotenv_path=env_path)
print("✅ .env loaded:", load_result)
print("DB:", os.environ.get("POSTGRES_DB"))
print("USER:", os.environ.get("POSTGRES_USER"))
print("PWD:", os.environ.get("POSTGRES_PASSWORD"))

app = Flask(__name__)
app.secret_key = 'key123'


@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        name = request.form["na"]
        password = request.form["ps"]
        money = int(request.form["ca"])

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template("signup.html", error="Username already taken.")

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (name, password, money) VALUES (%s, %s, %s)",
            (name, hashed_password, money)
        )
        conn.commit()
        session['username'] = name

        return redirect(url_for("main_screen"))
    else:
        return render_template("signup.html")

@app.route('/signin', methods=["POST", "GET"])
def signin():
    if request.method == "POST":
        name = request.form["na"]
        password = request.form["ps"]

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session['username'] = user['name']
            return redirect(url_for("main_screen"))
        else:
            return "Invalid name or password."

    else:
        return render_template("signin.html")

@app.route('/games')
def main_screen():
    if 'username' not in session:
        return redirect(url_for('signin'))

    username = session['username']

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT money FROM users WHERE name = %s", (username,))
    money = cursor.fetchone()["money"]

    return render_template("games.html", username=username, money=money)


@app.route('/blackjack', methods=['GET', 'POST'])
def blackjack():
    if 'username' not in session:
        return redirect(url_for('signin'))

    username = session['username']
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT money FROM users WHERE name = %s", (username,))
    money = cursor.fetchone()['money']
    error = None

    #  uploads the status of the game from -session (if there is)
    game_data = session.get('blackjack')
    game = None
    if game_data:
        game = BlackjackGame(
            bet=game_data['bet'],
            player=game_data['player'],
            dealer=game_data['dealer'],
            game_over=game_data['game_over'],
            result=game_data['result']
        )

    if request.method == 'POST':
        action = request.form.get('action')
        print("ACTION RECEIVED:", action)

        if action == 'start':
            try:
                bet = int(request.form['bet'])
            except ValueError:
                return render_template("blackjack.html", error="Invalid input", money=money)

            if bet <= 0 or bet > money:
                return render_template("blackjack.html", error="Invalid bet", money=money)

            game = BlackjackGame(bet)
            session['blackjack'] = {
                'bet': game.bet,
                'player': game.player,
                'dealer': game.dealer,
                'game_over': game.game_over,
                'result': game.result
            }

        elif action == 'hit' and game and not game.game_over:
            result = game.hit()
            if result == 'bust':
                game.result = {
                    'outcome': 'lose',
                    'player_total': game.calculate_total(game.player),
                    'dealer_total': game.calculate_total(game.dealer),
                    'new_money': money - game.bet
                }
                money -= game.bet
                cursor.execute("UPDATE users SET money = %s WHERE name = %s", (money, username))
                conn.commit()

        elif action == 'stand' and game and not game.game_over:
            outcome = game.stand()
            if outcome == 'win':
                money += game.bet
            elif outcome == 'lose':
                money -= game.bet
            # Draw – money stay the same

            game.result['new_money'] = money
            cursor.execute("UPDATE users SET money = %s WHERE name = %s", (money, username))
            conn.commit()

        #  updates the -session
        session['blackjack'] = {
            'bet': game.bet,
            'player': game.player,
            'dealer': game.dealer,
            'game_over': game.game_over,
            'result': game.result
        }

        return render_template("blackjack.html",
                               game=session['blackjack'],
                               error=error)

    return render_template("blackjack.html",
                           game=session.get('blackjack'),
                           money=money)

@app.route('/slots', methods=['GET', 'POST'])
def slots():
    if 'username' not in session:
        return redirect(url_for('signin'))

    result = None
    payout = 0
    error = None
    row = []

    if request.method == 'POST':
        try:
            bet = int(request.form['bet'])
            username = session['username']

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("SELECT money FROM users WHERE name = %s", (username,))
            user = cursor.fetchone()

            if not user or user['money'] < bet:
                error = "Insufficient funds"
            elif bet <= 0:
                error = "Bet must be greater than 0"
            else:
                new_balance = user['money'] - bet
                row = spin_row()
                payout = get_payout(row, bet)
                new_balance += payout

                cursor.execute("UPDATE users SET money = %s WHERE name = %s", (new_balance, username))
                conn.commit()

                result = {
                    'row': row,
                    'payout': payout,
                    'new_balance': new_balance
                }

        except ValueError:
            error = "Please enter a valid number"

    return render_template('slotMachine.html', result=result, error=error, payout=payout, row=row)

def deal_card():
    card = random.randint(1, 13)
    return 10 if card > 10 else card

def calculate_total(cards):
    total = sum(cards)
    # If there is an Ace (1), and it does not cause disqualification – we will count it as 11
    if 1 in cards and total + 10 <= 21:
        total += 10
    return total

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
