# app.py

from flask import Flask, render_template
from agentvsghosts import start_game

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/launch_game')
def launch_game():
    start_game()
    return 'Game launched!'

if __name__ == '__main__':
    app.run(debug=True)
