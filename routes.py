# routes.py

from flask import render_template
from agentvsghosts import run_game

def configure_routes(app):
    @app.route('/')
    def index():
        return render_template('game_page.html')

    @app.route('/launch_game')
    def launch_game():
        run_game()  # Call the function to execute game logic
        return 'Game launched!'
