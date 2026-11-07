import ast
import socket
import subprocess
import sys
import time

import requests


def read_request():
    node = ast.parse(input(), mode='eval').body
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == 'request' and len(node.args) == 2 and not node.keywords):
        raise ValueError('expected request(method, url)')
    return [ast.literal_eval(arg) for arg in node.args]


def main():
    method, url = read_request()
    with open('server.log', 'w') as log:
        server = subprocess.Popen([
            sys.executable, '-c',
            'from solution import app; '
            'app.run(host="127.0.0.1", port=7777, debug=False, use_reloader=False)',
        ], stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 8
            while True:
                if server.poll() is not None:
                    log.flush()
                    sys.stderr.write(open('server.log', encoding='utf-8').read())
                    raise RuntimeError(f'server exited with code {server.returncode}')
                try:
                    with socket.create_connection(('127.0.0.1', 7777), timeout=0.2):
                        break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError('server did not start')
                    time.sleep(0.05)
            response = requests.request(method, url, timeout=2)
            response.raise_for_status()
            with open('output.txt', 'wb') as output:
                output.write(response.content)
        finally:
            if server.poll() is None:
                server.terminate()
                try:
                    server.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


if __name__ == '__main__':
    main()
