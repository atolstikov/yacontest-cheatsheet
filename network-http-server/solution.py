from flask import Flask

app = Flask(__name__)


@app.route('/<a>/<b>')
def index(a, b):
    a, b = map(int, (a, b))
    return str(solve(a, b))


def solve(*data):
    return sum(data)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
