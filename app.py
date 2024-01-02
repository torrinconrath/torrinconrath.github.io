from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/')
def launch_game():
    subprocess.run(['python', 'path/to/agentvsghosts.py'])
    return 'Game launched!'

if __name__ == '__main__':
    app.run(debug=True)
