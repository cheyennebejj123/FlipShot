from flask import Flask, render_template
import csv
from collections import defaultdict

"""
Flask web application that displays a leaderboard from a CSV file.

The app reads player names, game modes, and scores from '../leaderboard.csv' and organizes
them into categories based on game mode. Each mode's scores are sorted in descending order 
to show the top performers.

Route:
    '/' - Loads and displays the leaderboard by rendering 'leaderboard.html', passing a dictionary
          where each key is a game mode and each value is a list of (name, score) tuples sorted by score.

Template:
    leaderboard.html 

Usage:
    Run the app and access it via http://localhost:5000/ or the host IP on port 5000.

Note:
    The app assumes the CSV file is structured with at least three columns: name, mode, score.
"""


app = Flask(__name__)

@app.route('/')
def leaderboard():
    leaderboard_data = defaultdict(list)

    with open('../leaderboard.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:
                name, mode, score = row[0], row[1], int(row[2])
                leaderboard_data[mode].append((name, score))

    for mode in leaderboard_data:
        leaderboard_data[mode].sort(key=lambda x: x[1], reverse=True)

    return render_template('leaderboard.html', leaderboard=leaderboard_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)