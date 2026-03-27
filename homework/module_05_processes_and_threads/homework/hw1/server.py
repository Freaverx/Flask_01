"""
Процесс, который займет порт 5000
"""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return "Server is running"


if __name__ == '__main__':
    app.run(port=5000, debug=False)