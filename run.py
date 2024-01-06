# run.py

from flask import Flask, render_template
from agentvsghosts import run_game  # Assuming this is where your Pygame logic is

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('game_page.html')

@app.route('/launch_game')
def launch_game():
    run_game()  # Call the function to execute game logic
    return 'Game launched!'

if __name__ == '__main__':
    app.run(debug=True)
