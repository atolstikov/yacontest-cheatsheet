from flask import Flask, jsonify, request
import hashlib

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_one_news():
    a = request.args.get('a', None)
    b = request.args.get('b', None)
    if a is None or b is None:
        print("Числа не найдены")
        return jsonify("")
    a, b = int(a), int(b)
    response = {
        'result': [a // b, a % b],
        'check': hashlib.sha256(bytes(abs(a) ^ abs(b))).hexdigest()
    }
    return jsonify(response)


def run():
    app.run(port=7777, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    run()
