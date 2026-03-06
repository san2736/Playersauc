# app.py

from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route("/")
def index():
    country = request.args.get("country")

    if country:
        cur.execute("SELECT * FROM players WHERE country=%s", (country,))
    else:
        cur.execute("SELECT * FROM players")

    players = cur.fetchall()
    return render_template("index.html", players=players)

@app.route("/player/<int:id>")
def player(id):

    cur.execute("SELECT * FROM players WHERE player_id=%s", (id,))
    player = cur.fetchone()

    cur.execute("SELECT MAX(bid_amount) FROM bids WHERE player_id=%s", (id,))
    bid = cur.fetchone()

    highest_bid = bid[0] if bid[0] else player[5]

    return render_template("player.html", player=player, highest_bid=highest_bid)

@app.route("/bid/<int:id>", methods=["POST"])
def bid(id):

    amount = int(request.form["amount"])
    bidder = request.form["bidder"]

    cur.execute("SELECT MAX(bid_amount) FROM bids WHERE player_id=%s", (id,))
    current = cur.fetchone()[0]

    if current is None:
        current = 0

    if amount > current:
        cur.execute(
            "INSERT INTO bids (player_id,bid_amount,bidder) VALUES (%s,%s,%s)",
            (id, amount, bidder)
        )
        conn.commit()

    return redirect(f"/player/{id}")

if __name__ == "__main__":
    app.run(debug=True)