# run.py

from flask import Flask, render_template, jsonify
from agentvsghosts import run_game  # Assuming this is where your Pygame logic is

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('game_page.html')

@app.route('/launch_game')
def launch_game():
    result = run_game()  # Call the function to execute game logic
    return jsonify({'message': f'Game launched! Result: {result}'})

if __name__ == '__main__':
    app.run(debug=True)
